use anyhow::{Context, Result};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::process::{Child, Command};
use tokio::time::{sleep, Duration};
use tracing::{info, warn};

#[derive(Clone)]
pub struct AgentDBClient {
    client: Client,
    base_url: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VectorQuery {
    pub vector: Vec<f32>,
    pub top_k: usize,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub filters: Option<serde_json::Value>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SearchResult {
    pub id: String,
    pub score: f32,
    pub metadata: serde_json::Value,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct StoreRequest {
    pub id: String,
    pub vector: Vec<f32>,
    pub metadata: serde_json::Value,
}

impl AgentDBClient {
    /// Create a new AgentDB client connecting to an existing server
    pub async fn new(base_url: String) -> Result<Self> {
        let client = Client::builder()
            .timeout(Duration::from_secs(30))
            .build()
            .context("Failed to create HTTP client")?;

        let agentdb = Self { client, base_url };

        // Test connection
        agentdb.health_check().await?;

        Ok(agentdb)
    }

    /// Spawn AgentDB server and create client
    pub async fn spawn(port: u16) -> Result<(Self, AgentDBProcess)> {
        info!("🧠 Spawning AgentDB server on port {}", port);

        let process = Command::new("npx")
            .args(["agentdb", "serve", "--port", &port.to_string()])
            .spawn()
            .context("Failed to spawn AgentDB server. Make sure Node.js/npx is installed.")?;

        // Wait for server to start
        sleep(Duration::from_secs(3)).await;

        let base_url = format!("http://localhost:{}", port);
        let client = Self::new(base_url).await?;

        Ok((client, AgentDBProcess { process: Some(process) }))
    }

    async fn health_check(&self) -> Result<()> {
        let url = format!("{}/health", self.base_url);

        for attempt in 1..=5 {
            match self.client.get(&url).send().await {
                Ok(_) => {
                    info!("✅ AgentDB connection successful");
                    return Ok(());
                }
                Err(e) if attempt < 5 => {
                    warn!("AgentDB connection attempt {} failed: {}", attempt, e);
                    sleep(Duration::from_secs(1)).await;
                }
                Err(e) => {
                    return Err(e).context("Failed to connect to AgentDB after 5 attempts");
                }
            }
        }

        unreachable!()
    }

    /// Store a vector with metadata in AgentDB
    pub async fn store_opportunity(
        &self,
        id: &str,
        embedding: Vec<f32>,
        metadata: serde_json::Value,
    ) -> Result<()> {
        let url = format!("{}/api/vectors/store", self.base_url);

        let request = StoreRequest {
            id: id.to_string(),
            vector: embedding,
            metadata,
        };

        self.client
            .post(&url)
            .json(&request)
            .send()
            .await
            .context("Failed to store vector in AgentDB")?
            .error_for_status()
            .context("AgentDB returned error status")?;

        Ok(())
    }

    /// Search for similar vectors
    pub async fn search_similar(&self, query: VectorQuery) -> Result<Vec<SearchResult>> {
        let url = format!("{}/api/vectors/search", self.base_url);

        let response = self
            .client
            .post(&url)
            .json(&query)
            .send()
            .await
            .context("Failed to search vectors in AgentDB")?
            .error_for_status()
            .context("AgentDB search returned error")?;

        let results: Vec<SearchResult> = response
            .json()
            .await
            .context("Failed to parse AgentDB search results")?;

        Ok(results)
    }

    /// Use AgentDB reasoning capabilities
    pub async fn reason_about_pattern(&self, pattern_description: &str) -> Result<String> {
        let url = format!("{}/api/reasoning/analyze", self.base_url);

        let body = serde_json::json!({
            "query": pattern_description,
            "context": "monetization_opportunities",
        });

        let response = self
            .client
            .post(&url)
            .json(&body)
            .send()
            .await
            .context("Failed to send reasoning query to AgentDB")?
            .error_for_status()
            .context("AgentDB reasoning returned error")?;

        let result: serde_json::Value = response
            .json()
            .await
            .context("Failed to parse reasoning response")?;

        Ok(result["reasoning"]
            .as_str()
            .unwrap_or("No reasoning provided")
            .to_string())
    }

    /// Batch search for multiple queries
    pub async fn batch_search(&self, queries: Vec<VectorQuery>) -> Result<Vec<Vec<SearchResult>>> {
        let url = format!("{}/api/vectors/batch-search", self.base_url);

        let response = self
            .client
            .post(&url)
            .json(&queries)
            .send()
            .await
            .context("Failed to batch search in AgentDB")?
            .error_for_status()
            .context("AgentDB batch search returned error")?;

        let results: Vec<Vec<SearchResult>> = response
            .json()
            .await
            .context("Failed to parse batch search results")?;

        Ok(results)
    }
}

/// Handle to manage AgentDB server process lifecycle
pub struct AgentDBProcess {
    process: Option<Child>,
}

impl Drop for AgentDBProcess {
    fn drop(&mut self) {
        if let Some(mut process) = self.process.take() {
            info!("🛑 Shutting down AgentDB server");
            let _ = process.kill();
        }
    }
}
