use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tracing::{info, warn};

use super::client::{AgentDBClient, VectorQuery};

#[derive(Debug, Serialize, Deserialize)]
pub struct OpportunityData {
    pub rank: Option<u32>,
    pub project: String,
    pub owner: OwnerInfo,
    pub repository: RepositoryInfo,
    pub monetization: MonetizationInfo,
    pub market_analysis: Option<MarketAnalysis>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OwnerInfo {
    pub username: String,
    pub company: Option<String>,
    pub location: Option<String>,
    pub followers: Option<u32>,
    pub profile_url: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RepositoryInfo {
    pub name: String,
    pub url: String,
    pub stars: u32,
    pub description: String,
    pub language: String,
    pub category: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MonetizationInfo {
    pub strategies: Vec<String>,
    pub revenue_potential_score: f32,
    pub time_to_market: String,
    pub required_investment: String,
    pub estimated_annual_revenue: String,
    pub why_fast: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MarketAnalysis {
    pub target_customers: String,
    pub market_size: String,
    pub competition: String,
    pub barriers_to_entry: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TrainingDataFile {
    pub report_metadata: ReportMetadata,
    pub top_15_fast_money_makers: Vec<OpportunityData>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ReportMetadata {
    pub analysis_date: String,
    pub total_stargazers: u32,
    pub qualified_users: u32,
    pub high_potential_projects: u32,
    pub total_portfolio_value: String,
    pub recommended_initial_investment: String,
}

/// Generates a simple text embedding using character-based features
/// This is a placeholder - in production, use a real embedding model
pub fn generate_simple_embedding(text: &str) -> Vec<f32> {
    let mut embedding = vec![0.0f32; 128]; // Simple 128-dim embedding

    // Simple feature extraction
    let words: Vec<&str> = text.to_lowercase().split_whitespace().collect();
    let char_count = text.len() as f32;
    let word_count = words.len() as f32;

    // Dimension 0-9: Basic text statistics
    embedding[0] = (char_count / 1000.0).min(1.0); // Normalized length
    embedding[1] = (word_count / 100.0).min(1.0); // Normalized word count
    embedding[2] = if text.contains("AI") || text.contains("ML") { 0.8 } else { 0.0 };
    embedding[3] = if text.contains("security") || text.contains("cyber") { 0.8 } else { 0.0 };
    embedding[4] = if text.contains("platform") || text.contains("service") { 0.7 } else { 0.0 };
    embedding[5] = if text.contains("API") || text.contains("SDK") { 0.7 } else { 0.0 };
    embedding[6] = if text.contains("enterprise") { 0.9 } else { 0.0 };
    embedding[7] = if text.contains("SaaS") || text.contains("cloud") { 0.8 } else { 0.0 };
    embedding[8] = if text.contains("developer") || text.contains("DevOps") { 0.7 } else { 0.0 };
    embedding[9] = if text.contains("analytics") || text.contains("monitoring") { 0.7 } else { 0.0 };

    // Dimension 10-127: Keyword-based features
    let keywords = [
        "python", "javascript", "go", "rust", "java",
        "api", "framework", "library", "tool", "platform",
        "security", "authentication", "encryption", "privacy",
        "ai", "ml", "llm", "gpt", "neural",
        "database", "sql", "nosql", "redis", "postgres",
        "web", "mobile", "desktop", "cli", "gui",
        "devops", "cicd", "kubernetes", "docker", "cloud",
        "monitoring", "logging", "analytics", "metrics",
        "automation", "testing", "deployment", "integration",
        "open-source", "enterprise", "saas", "freemium",
    ];

    for (i, keyword) in keywords.iter().enumerate() {
        if i + 10 < 128 {
            embedding[i + 10] = if text.to_lowercase().contains(keyword) { 0.5 } else { 0.0 };
        }
    }

    // Normalize to unit vector
    let magnitude: f32 = embedding.iter().map(|x| x * x).sum::<f32>().sqrt();
    if magnitude > 0.0 {
        for val in embedding.iter_mut() {
            *val /= magnitude;
        }
    }

    embedding
}

/// Generate embedding for an opportunity
pub fn generate_opportunity_embedding(opp: &OpportunityData) -> Vec<f32> {
    // Combine all relevant text fields
    let combined_text = format!(
        "{} {} {} {} {} {} {}",
        opp.repository.name,
        opp.repository.description,
        opp.repository.category,
        opp.repository.language,
        opp.monetization.why_fast,
        opp.monetization.strategies.join(" "),
        opp.market_analysis
            .as_ref()
            .map(|m| m.target_customers.clone())
            .unwrap_or_default()
    );

    generate_simple_embedding(&combined_text)
}

/// Train AgentDB on existing opportunities
pub async fn train_on_opportunities(
    client: &AgentDBClient,
    opportunities: Vec<OpportunityData>,
) -> Result<()> {
    info!("🎓 Training AgentDB on {} opportunities", opportunities.len());

    let mut success_count = 0;
    let mut error_count = 0;

    for opp in opportunities {
        // Generate embedding
        let embedding = generate_opportunity_embedding(&opp);

        // Prepare metadata
        let metadata = serde_json::json!({
            "project": opp.project,
            "owner": opp.owner.username,
            "company": opp.owner.company,
            "location": opp.owner.location,
            "stars": opp.repository.stars,
            "language": opp.repository.language,
            "category": opp.repository.category,
            "description": opp.repository.description,
            "revenue_score": opp.monetization.revenue_potential_score,
            "estimated_revenue": opp.monetization.estimated_annual_revenue,
            "time_to_market": opp.monetization.time_to_market,
            "investment_needed": opp.monetization.required_investment,
            "strategies": opp.monetization.strategies,
            "why_fast": opp.monetization.why_fast,
            "url": opp.repository.url,
        });

        // Store in AgentDB
        let id = format!("{}/{}", opp.owner.username, opp.repository.name);

        match client.store_opportunity(&id, embedding, metadata).await {
            Ok(_) => {
                success_count += 1;
                if success_count % 10 == 0 {
                    info!("✅ Stored {}/{} opportunities", success_count, success_count + error_count);
                }
            }
            Err(e) => {
                warn!("❌ Failed to store {}: {}", id, e);
                error_count += 1;
            }
        }
    }

    info!("🎓 Training complete: {} successful, {} errors", success_count, error_count);

    Ok(())
}

/// Validate training by testing similarity search
pub async fn validate_training(
    client: &AgentDBClient,
    test_opportunities: &[OpportunityData],
) -> Result<f32> {
    info!("🧪 Validating training quality...");

    let mut correct = 0;
    let mut total = 0;

    for test_opp in test_opportunities.iter().take(10) {
        let embedding = generate_opportunity_embedding(test_opp);

        // Search for similar opportunities
        let results = client
            .search_similar(VectorQuery {
                vector: embedding,
                top_k: 5,
                filters: None,
            })
            .await?;

        // Check if the top result is in the same category
        if let Some(top_result) = results.first() {
            let result_category = top_result.metadata["category"]
                .as_str()
                .unwrap_or("");

            if result_category == test_opp.repository.category {
                correct += 1;
            }
        }

        total += 1;
    }

    let accuracy = correct as f32 / total as f32;
    info!("✅ Training validation accuracy: {:.1}%", accuracy * 100.0);

    Ok(accuracy)
}

/// Extract patterns from trained opportunities
pub async fn extract_patterns(
    client: &AgentDBClient,
) -> Result<HashMap<String, Vec<String>>> {
    info!("🔍 Extracting success patterns from AgentDB...");

    // Query AgentDB reasoning about patterns
    let pattern_query = "Analyze all stored opportunities and identify:\n\
        1. Common characteristics of high-revenue projects (score > 8)\n\
        2. Which programming languages are most monetizable\n\
        3. What categories have fastest time-to-market\n\
        4. Common monetization strategies that work";

    let reasoning = client.reason_about_pattern(pattern_query).await?;

    info!("🧠 AgentDB Reasoning:\n{}", reasoning);

    // Parse patterns (in production, use structured output)
    let mut patterns = HashMap::new();
    patterns.insert("reasoning".to_string(), vec![reasoning]);

    Ok(patterns)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_embedding() {
        let text = "AI-powered security platform for enterprise";
        let embedding = generate_simple_embedding(text);

        assert_eq!(embedding.len(), 128);
        assert!(embedding[2] > 0.0); // Should detect "AI"
        assert!(embedding[3] > 0.0); // Should detect "security"
        assert!(embedding[6] > 0.0); // Should detect "enterprise"
    }

    #[test]
    fn test_embedding_normalization() {
        let text = "Test text";
        let embedding = generate_simple_embedding(text);

        // Check if normalized (magnitude ~1.0)
        let magnitude: f32 = embedding.iter().map(|x| x * x).sum::<f32>().sqrt();
        assert!((magnitude - 1.0).abs() < 0.01);
    }
}
