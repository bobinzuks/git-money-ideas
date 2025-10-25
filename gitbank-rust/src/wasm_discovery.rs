//! 🚀 WASM Infinite Discovery Engine
//!
//! Process millions of repos in the browser with:
//! - Advanced 256-feature embeddings
//! - Multi-factor fast-money scoring
//! - Real-time vector similarity search
//! - Zero backend dependencies

#![cfg(target_arch = "wasm32")]

use wasm_bindgen::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
}

macro_rules! console_log {
    ($($t:tt)*) => (log(&format_args!($($t)*).to_string()))
}

/// Repository data structure
#[derive(Debug, Clone, Serialize, Deserialize)]
#[wasm_bindgen(getter_with_clone)]
pub struct Repository {
    pub name: String,
    pub owner: String,
    pub description: String,
    pub stars: u32,
    pub forks: u32,
    pub language: String,
    pub category: String,
    #[wasm_bindgen(skip)]
    pub topics: Vec<String>,
    pub url: String,
}

#[wasm_bindgen]
impl Repository {
    #[wasm_bindgen(constructor)]
    pub fn new(
        name: String,
        owner: String,
        description: String,
        stars: u32,
        forks: u32,
        language: String,
        url: String,
    ) -> Self {
        let category = categorize_repository(&description, &[]);

        Self {
            name,
            owner,
            description,
            stars,
            forks,
            language,
            category,
            topics: Vec::new(),
            url,
        }
    }

    #[wasm_bindgen(js_name = setTopics)]
    pub fn set_topics(&mut self, topics: JsValue) {
        if let Ok(topics_vec) = serde_wasm_bindgen::from_value::<Vec<String>>(topics) {
            self.topics = topics_vec;
        }
    }

    #[wasm_bindgen(js_name = getTopics)]
    pub fn get_topics(&self) -> JsValue {
        serde_wasm_bindgen::to_value(&self.topics).unwrap_or(JsValue::NULL)
    }
}

/// Fast-money opportunity with scoring details
#[derive(Debug, Clone, Serialize, Deserialize)]
#[wasm_bindgen(getter_with_clone)]
pub struct Opportunity {
    #[wasm_bindgen(skip)]
    pub repository: Repository,
    pub fast_money_score: f64,
    pub demand_score: f64,
    pub competition_score: f64,
    pub ease_score: f64,
    pub revenue_score: f64,
    pub revenue_estimate_low: u32,
    pub revenue_estimate_high: u32,
    pub time_to_market_days: u32,
    pub risk_level: String,
}

#[wasm_bindgen]
impl Opportunity {
    #[wasm_bindgen(js_name = getRepository)]
    pub fn get_repository(&self) -> JsValue {
        serde_wasm_bindgen::to_value(&self.repository).unwrap_or(JsValue::NULL)
    }
}

/// Advanced embedding generator (256 dimensions)
pub struct AdvancedEmbedding;

impl AdvancedEmbedding {
    const DIMENSION: usize = 256;

    /// Generate 256-dimensional embedding with structured features
    pub fn generate(repo: &Repository) -> Vec<f32> {
        let mut vec = vec![0.0f32; Self::DIMENSION];

        let combined_text = format!(
            "{} {} {} {}",
            repo.name.to_lowercase(),
            repo.description.to_lowercase(),
            repo.category.to_lowercase(),
            repo.topics.join(" ").to_lowercase()
        );

        // Feature 0-9: Category signals
        let categories = [
            ("security", vec!["security", "pentest", "vulnerability", "exploit"]),
            ("ai_ml", vec!["ai", "ml", "machine-learning", "llm", "gpt"]),
            ("devops", vec!["kubernetes", "docker", "ci/cd", "deployment"]),
            ("api", vec!["api", "rest", "graphql", "sdk", "framework"]),
            ("analytics", vec!["analytics", "dashboard", "visualization", "metrics"]),
            ("database", vec!["database", "sql", "nosql", "storage", "cache"]),
            ("saas", vec!["saas", "platform", "service", "hosted", "cloud"]),
            ("enterprise", vec!["enterprise", "b2b", "corporate", "business"]),
            ("monitoring", vec!["monitoring", "observability", "logging", "tracing"]),
            ("automation", vec!["automation", "workflow", "pipeline", "orchestration"]),
        ];

        for (idx, (_, keywords)) in categories.iter().enumerate() {
            let score: f32 = keywords.iter()
                .filter(|kw| combined_text.contains(*kw))
                .count() as f32;
            vec[idx] = (score / 3.0).tanh();
        }

        // Feature 10-19: Monetization signals
        let monetization_keywords = [
            "enterprise", "commercial", "professional", "premium", "pro",
            "business", "license", "subscription", "saas", "hosting"
        ];

        for (i, keyword) in monetization_keywords.iter().enumerate() {
            if combined_text.contains(keyword) {
                vec[10 + i] = 1.0;
            }
        }

        // Feature 20-29: Repository metrics (normalized)
        vec[20] = (repo.stars as f32).ln_1p() / 10.0;
        vec[21] = (repo.forks as f32).ln_1p() / 10.0;

        // Fork/star ratio
        if repo.stars > 0 {
            vec[22] = ((repo.forks as f32) / (repo.stars as f32)).min(1.0);
        }

        // Star tiers
        vec[23] = if repo.stars >= 10000 { 1.0 } else { 0.0 };
        vec[24] = if repo.stars >= 5000 { 1.0 } else { 0.0 };
        vec[25] = if repo.stars >= 1000 { 1.0 } else { 0.0 };
        vec[26] = if repo.stars >= 500 { 1.0 } else { 0.0 };

        // Feature 27-29: Language signals
        let high_value_langs = ["go", "rust", "java", "python", "typescript"];
        vec[27] = if high_value_langs.contains(&repo.language.to_lowercase().as_str()) {
            1.0
        } else {
            0.5
        };

        // Feature 30-39: Topic embeddings
        for (i, topic) in repo.topics.iter().take(10).enumerate() {
            vec[30 + i] = 1.0;
            // Hash-based variation
            vec[30 + i] *= (topic.len() as f32 / 20.0).min(1.0);
        }

        // Feature 40-89: Character n-grams from description (50 features)
        for (i, ch) in repo.description.chars().take(50).enumerate() {
            vec[40 + i] = (ch as u32 as f32) / 127.0;
        }

        // Feature 90-189: Word hash embeddings (100 features)
        let words: Vec<&str> = combined_text.split_whitespace().collect();
        for word in words.iter().take(100) {
            let hash = simple_hash(word) % 100;
            vec[90 + hash] += 0.1;
        }

        // Feature 190-199: Description length features
        vec[190] = (repo.description.len() as f32 / 500.0).min(1.0);
        vec[191] = (repo.name.len() as f32 / 50.0).min(1.0);

        // Feature 200-255: Reserved for future enhancements

        // Normalize to unit length
        let norm: f32 = vec.iter().map(|x| x * x).sum::<f32>().sqrt();
        if norm > 0.0 {
            for x in &mut vec {
                *x /= norm;
            }
        }

        vec
    }
}

/// Fast-money scorer
pub struct FastMoneyScorer;

impl FastMoneyScorer {
    /// Score repository for fast-money potential
    pub fn score(repo: &Repository) -> Opportunity {
        let mut demand_score = 0.0;
        let mut competition_score = 0.0;
        let mut ease_score = 0.0;
        let mut revenue_score = 0.0;

        // 1. Market Demand (0-3)
        demand_score += match repo.stars {
            s if s >= 5000 => 3.0,
            s if s >= 2000 => 2.5,
            s if s >= 1000 => 2.0,
            s if s >= 500 => 1.5,
            s if s >= 100 => 1.0,
            _ => 0.5,
        };

        // High fork ratio = active community
        if repo.stars > 0 && (repo.forks as f64 / repo.stars as f64) > 0.3 {
            demand_score += 0.5;
        }

        // 2. Competition Analysis (0-2)
        if repo.stars < 5000 {
            competition_score += 1.0;
        }
        if repo.stars > 500 {
            competition_score += 1.0;
        }

        // 3. Ease of Monetization (0-3)
        let enterprise_categories = ["security", "devops", "analytics", "database", "ai"];
        if enterprise_categories.iter().any(|c| repo.category.to_lowercase().contains(c)) {
            ease_score += 1.5;
        }

        let text = format!("{} {}", repo.description.to_lowercase(), repo.topics.join(" ").to_lowercase());
        let monetization_keywords = ["api", "saas", "platform", "service", "enterprise"];
        let keyword_count = monetization_keywords.iter()
            .filter(|kw| text.contains(*kw))
            .count();
        ease_score += (keyword_count as f64 * 0.5).min(1.5);

        // 4. Revenue Potential (0-2)
        let high_value_langs = ["go", "rust", "java", "python", "typescript"];
        if high_value_langs.contains(&repo.language.to_lowercase().as_str()) {
            revenue_score += 1.0;
        }

        if repo.category.to_lowercase().contains("security") || text.contains("enterprise") {
            revenue_score += 1.0;
        }

        let total_score = demand_score + competition_score + ease_score + revenue_score;

        // Estimate revenue
        let (low, high) = estimate_revenue(repo.stars, &repo.category, total_score);

        // Time to market
        let time_to_market_days = match total_score {
            s if s >= 8.5 => 45,
            s if s >= 7.5 => 90,
            s if s >= 6.5 => 135,
            _ => 270,
        };

        // Risk assessment
        let risk_level = if repo.stars < 500 || total_score < 6.0 {
            "High"
        } else if repo.stars < 2000 || total_score < 7.5 {
            "Medium"
        } else {
            "Low"
        }.to_string();

        Opportunity {
            repository: repo.clone(),
            fast_money_score: (total_score * 10.0).round() / 10.0,
            demand_score: (demand_score * 10.0).round() / 10.0,
            competition_score: (competition_score * 10.0).round() / 10.0,
            ease_score: (ease_score * 10.0).round() / 10.0,
            revenue_score: (revenue_score * 10.0).round() / 10.0,
            revenue_estimate_low: low,
            revenue_estimate_high: high,
            time_to_market_days,
            risk_level,
        }
    }
}

/// In-memory vector database for WASM
#[wasm_bindgen]
pub struct VectorDatabase {
    embeddings: Vec<Vec<f32>>,
    metadata: Vec<Opportunity>,
}

#[wasm_bindgen]
impl VectorDatabase {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        console_log!("🚀 Initializing WASM Vector Database");
        Self {
            embeddings: Vec::new(),
            metadata: Vec::new(),
        }
    }

    /// Store repository with embedding
    #[wasm_bindgen]
    pub fn store(&mut self, repo: Repository) -> f64 {
        // Generate embedding
        let embedding = AdvancedEmbedding::generate(&repo);

        // Score for fast-money potential
        let opportunity = FastMoneyScorer::score(&repo);
        let score = opportunity.fast_money_score;

        // Store
        self.embeddings.push(embedding);
        self.metadata.push(opportunity);

        score
    }

    /// Search for similar repositories
    #[wasm_bindgen(js_name = searchSimilar)]
    pub fn search_similar(&self, repo: Repository, top_k: usize) -> JsValue {
        let query_embedding = AdvancedEmbedding::generate(&repo);

        let mut results: Vec<(usize, f32)> = self.embeddings
            .iter()
            .enumerate()
            .map(|(idx, emb)| {
                let similarity = cosine_similarity(&query_embedding, emb);
                (idx, similarity)
            })
            .collect();

        results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

        let top_results: Vec<_> = results
            .into_iter()
            .take(top_k)
            .map(|(idx, sim)| {
                let mut map = HashMap::new();
                map.insert("similarity", sim as f64);
                map.insert("score", self.metadata[idx].fast_money_score);
                map.insert("index", idx as f64);
                map
            })
            .collect();

        serde_wasm_bindgen::to_value(&top_results).unwrap_or(JsValue::NULL)
    }

    /// Get top fast-money opportunities
    #[wasm_bindgen(js_name = getTopOpportunities)]
    pub fn get_top_opportunities(&self, limit: usize) -> JsValue {
        let mut opportunities: Vec<_> = self.metadata
            .iter()
            .enumerate()
            .collect();

        opportunities.sort_by(|a, b| {
            b.1.fast_money_score
                .partial_cmp(&a.1.fast_money_score)
                .unwrap()
        });

        let top: Vec<_> = opportunities
            .into_iter()
            .take(limit)
            .map(|(_, opp)| opp)
            .collect();

        serde_wasm_bindgen::to_value(&top).unwrap_or(JsValue::NULL)
    }

    /// Get database statistics
    #[wasm_bindgen(js_name = getStats)]
    pub fn get_stats(&self) -> JsValue {
        let total = self.metadata.len();
        let avg_score = if total > 0 {
            self.metadata.iter().map(|o| o.fast_money_score).sum::<f64>() / total as f64
        } else {
            0.0
        };

        let fast_money_count = self.metadata
            .iter()
            .filter(|o| o.fast_money_score >= 7.0)
            .count();

        // Create a proper JavaScript object
        let obj = js_sys::Object::new();

        js_sys::Reflect::set(
            &obj,
            &JsValue::from_str("total"),
            &JsValue::from_f64(total as f64),
        ).unwrap();

        js_sys::Reflect::set(
            &obj,
            &JsValue::from_str("avg_score"),
            &JsValue::from_f64(avg_score),
        ).unwrap();

        js_sys::Reflect::set(
            &obj,
            &JsValue::from_str("fast_money_count"),
            &JsValue::from_f64(fast_money_count as f64),
        ).unwrap();

        obj.into()
    }

    #[wasm_bindgen(js_name = getCount)]
    pub fn get_count(&self) -> usize {
        self.metadata.len()
    }
}

// Helper functions

fn categorize_repository(description: &str, topics: &[String]) -> String {
    let text = format!(
        "{} {}",
        description.to_lowercase(),
        topics.join(" ").to_lowercase()
    );

    if text.contains("security") || text.contains("pentest") || text.contains("vulnerability") {
        "Security Tools".to_string()
    } else if text.contains("ai") || text.contains("ml") || text.contains("machine learning") {
        "AI/ML Tools".to_string()
    } else if text.contains("devops") || text.contains("kubernetes") || text.contains("deployment") {
        "DevOps Tools".to_string()
    } else if text.contains("api") || text.contains("framework") || text.contains("library") {
        "Developer Framework".to_string()
    } else if text.contains("analytics") || text.contains("dashboard") || text.contains("monitoring") {
        "Analytics Platform".to_string()
    } else if text.contains("database") || text.contains("storage") || text.contains("sql") {
        "Database Technology".to_string()
    } else {
        "General Software".to_string()
    }
}

fn estimate_revenue(stars: u32, category: &str, score: f64) -> (u32, u32) {
    let multiplier = match category.to_lowercase().as_str() {
        c if c.contains("security") => 200,
        c if c.contains("ai") => 300,
        c if c.contains("devops") => 150,
        c if c.contains("analytics") => 180,
        c if c.contains("database") => 250,
        _ => 100,
    };

    let low = (stars * multiplier * 5 / 100) as u32;
    let high = ((stars * multiplier) as f64 * 0.3 * (score / 10.0)) as u32;

    (low, high)
}

fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
    let dot: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
    dot // Vectors already normalized
}

fn simple_hash(s: &str) -> usize {
    s.bytes().map(|b| b as usize).sum()
}

#[wasm_bindgen(start)]
pub fn main() {
    console_log!("🚀 WASM Discovery Engine initialized!");
}
