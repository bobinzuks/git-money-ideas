# WASM-Based Infinite Repository Discovery System
## Architecture Design Document

**Version:** 1.0
**Date:** 2025-10-24
**Status:** Design Phase
**Target:** Production-Ready WASM System for Autonomous GitHub Discovery

---

## Executive Summary

This document outlines a revolutionary WASM-based system that discovers infinite repositories through GitHub's social graph by following "success paths" - branches with high commercial potential. The system continuously learns from discoveries to improve pattern recognition, creating a self-improving discovery engine.

**Key Innovation:** Instead of static searches, we traverse GitHub's social graph dynamically, following users who star successful repositories, discovering their projects, and recursively expanding through high-value branches.

**Expected Performance:**
- Discovery Rate: 500-2,000 repos/hour (per WASM instance)
- Pattern Accuracy: 70-85% after training on 50+ opportunities
- Scalability: Linear with number of WASM instances
- Cost: Near-zero (client-side execution, GitHub API free tier)

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Graph Traversal Algorithm](#graph-traversal-algorithm)
3. [WASM Module Design](#wasm-module-design)
4. [AgentDB Integration](#agentdb-integration)
5. [Data Flow Pipeline](#data-flow-pipeline)
6. [Deployment Strategy](#deployment-strategy)
7. [Performance Optimization](#performance-optimization)
8. [Storage Strategy](#storage-strategy)
9. [Implementation Roadmap](#implementation-roadmap)

---

## System Architecture

### High-Level Architecture (ASCII)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INFINITE DISCOVERY SYSTEM                         │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   GitHub API     │◄────────│   WASM Core      │────────►│    AgentDB       │
│   (Rate Limited) │         │   Graph Engine   │         │   Pattern DB     │
└──────────────────┘         └──────────────────┘         └──────────────────┘
         │                            │                            │
         │                            │                            │
         ▼                            ▼                            ▼
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  Stargazers      │         │  Priority Queue  │         │  Success Scores  │
│  Repositories    │────────►│  (BFS/DFS)       │────────►│  Pattern Match   │
│  User Profiles   │         │  Visited Set     │         │  Embeddings      │
└──────────────────┘         └──────────────────┘         └──────────────────┘
         │                            │                            │
         │                            │                            │
         ▼                            ▼                            ▼
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  Branch Pruning  │         │  Success Filter  │         │  Training Loop   │
│  Low-Value Paths │────────►│  Score Threshold │────────►│  Update Patterns │
│  Cycle Detection │         │  Commercial Test │         │  Refine Weights  │
└──────────────────┘         └──────────────────┘         └──────────────────┘
         │                            │                            │
         └────────────────────────────┴────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DISCOVERED OPPORTUNITIES                          │
│  ├─ IndexedDB (Browser) or SQLite WASM (Node.js/CLI)               │
│  ├─ Deduplication via Bloom Filters                                 │
│  ├─ Real-time sync to AgentDB                                       │
│  └─ Export to JSON/CSV for manual review                            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT OPTIONS                                │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │  Browser    │  │  Node.js    │  │  CLI Tool   │  │  Service  │ │
│  │  Extension  │  │  Script     │  │  (Rust)     │  │  Worker   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. **WASM Core (Rust → WASM)**
- **Purpose:** High-performance graph traversal engine
- **Size:** ~500KB compressed
- **Languages:** Rust compiled to WASM
- **Key Features:**
  - Priority queue for BFS/DFS
  - Visited set for cycle detection
  - Bloom filter for deduplication
  - Success scoring algorithm
  - Rate limit management

#### 2. **GitHub API Layer**
- **Purpose:** Fetch stargazers, repos, user profiles
- **Rate Limits:**
  - Authenticated: 5,000 requests/hour
  - Unauthenticated: 60 requests/hour
- **Endpoints Used:**
  - `/repos/{owner}/{repo}/stargazers` (100/page)
  - `/users/{username}/repos` (100/page)
  - `/repos/{owner}/{repo}` (details)
- **Strategy:** Aggressive caching, multi-token rotation

#### 3. **AgentDB Integration**
- **Purpose:** Pattern learning and opportunity scoring
- **Embedding Model:** 128-dim simplified embeddings (upgradeable to sentence-transformers)
- **Vector Storage:** In-memory HNSW index (10K+ vectors)
- **Reasoning Engine:** Pattern extraction via LLM integration
- **Training Loop:** Continuous learning from validated discoveries

#### 4. **Storage Layer**
- **Browser:** IndexedDB (50MB+ quota)
- **Node.js:** SQLite WASM (unlimited)
- **CLI:** File-based JSON/SQLite
- **Schema:**
  - Discovered repos (deduplicated)
  - Graph edges (user → repo → stargazer)
  - Success scores
  - Visit history

---

## Graph Traversal Algorithm

### Concept: Success Path Traversal

The algorithm follows "success branches" through GitHub's social graph:

```
User stars Repo A (seed)
    │
    └──► Get stargazers of Repo A
            │
            ├──► User 1
            │     └──► Get User 1's repos [B, C, D]
            │           │
            │           ├──► Score repos B, C, D
            │           │     └──► If score > threshold:
            │           │           ├──► Add to queue (priority by score)
            │           │           └──► Recurse: Get stargazers of B, C, D
            │           │
            │           └──► If score < threshold:
            │                 └──► Prune branch (stop recursion)
            │
            ├──► User 2
            │     └──► Get User 2's repos [E, F]
            │           └──► (repeat scoring & recursion)
            │
            └──► User N...
```

### Algorithm Pseudocode

```rust
// Main discovery loop
async fn discover_infinite_repos(
    seed_repos: Vec<String>,
    agentdb: &AgentDBClient,
    github: &GitHubClient,
) -> Result<()> {
    // Priority queue: (score, repo_id)
    let mut queue = BinaryHeap::new();
    let mut visited = HashSet::new();
    let mut bloom_filter = BloomFilter::new(1_000_000, 0.01); // 1M capacity, 1% false positive

    // Initialize with seed repos
    for repo in seed_repos {
        queue.push((10.0, repo)); // Max priority for seeds
    }

    while let Some((priority, repo_id)) = queue.pop() {
        // Skip if already visited
        if visited.contains(&repo_id) || bloom_filter.contains(&repo_id) {
            continue;
        }

        visited.insert(repo_id.clone());
        bloom_filter.insert(&repo_id);

        // Fetch repository details
        let repo = github.get_repo(&repo_id).await?;

        // Score repository using AgentDB
        let score = agentdb.score_repository(&repo).await?;

        // Store if high-value (score > threshold)
        if score >= SUCCESS_THRESHOLD {
            store_opportunity(&repo, score).await?;

            // Train AgentDB on this discovery (continuous learning)
            agentdb.train_incremental(&repo, score).await?;
        }

        // Prune low-value branches (stop recursion early)
        if score < PRUNE_THRESHOLD {
            log::info!("Pruning branch: {} (score: {})", repo_id, score);
            continue;
        }

        // Get stargazers of this repo
        let stargazers = github.get_stargazers(&repo_id, MAX_STARGAZERS).await?;

        // For each stargazer, discover their repos
        for user in stargazers {
            let user_repos = github.get_user_repos(&user.login).await?;

            for user_repo in user_repos {
                let repo_key = format!("{}/{}", user_repo.owner, user_repo.name);

                // Skip if already visited
                if visited.contains(&repo_key) || bloom_filter.contains(&repo_key) {
                    continue;
                }

                // Quick pre-filter (avoid API calls for obvious low-value repos)
                let pre_score = quick_score(&user_repo);

                if pre_score >= PRE_FILTER_THRESHOLD {
                    // Calculate priority based on:
                    // - Current repo's score (parent influence)
                    // - Pre-score of discovered repo
                    // - Star count (weak signal)
                    let priority = calculate_priority(score, pre_score, user_repo.stars);

                    queue.push((priority, repo_key));
                }
            }
        }

        // Rate limit management
        rate_limiter.wait_if_needed().await?;
    }

    Ok(())
}

// Success scoring (AgentDB-powered)
async fn score_repository(agentdb: &AgentDBClient, repo: &Repository) -> Result<f32> {
    // Generate embedding for this repo
    let embedding = generate_embedding(repo);

    // Find similar successful repos in AgentDB
    let similar = agentdb.search_similar(embedding, top_k=10).await?;

    // Calculate weighted score based on similarity to known successes
    let mut score = 0.0;
    let mut total_weight = 0.0;

    for result in similar {
        let similarity = result.score;
        let known_revenue_score = result.metadata["revenue_score"].as_f64().unwrap_or(0.0);

        score += similarity * known_revenue_score;
        total_weight += similarity;
    }

    if total_weight > 0.0 {
        score /= total_weight;
    }

    // Boost/penalize based on repo characteristics
    score *= repo_quality_multiplier(repo);

    // Normalize to 0-10 scale
    score.min(10.0).max(0.0)
}

// Quick pre-filter (no API calls, just metadata)
fn quick_score(repo: &RepositoryMetadata) -> f32 {
    let mut score = 5.0; // Baseline

    // Star count signal (logarithmic)
    score += (repo.stars as f32).log10() * 0.5;

    // Language signal
    if VALUABLE_LANGUAGES.contains(&repo.language.as_str()) {
        score += 1.0;
    }

    // Keywords in description
    if has_commercial_keywords(&repo.description) {
        score += 1.0;
    }

    // Active maintenance (updated recently)
    if repo.updated_within_days(90) {
        score += 0.5;
    }

    // Fork ratio (too high = not original)
    if repo.forks as f32 / repo.stars as f32 > 0.3 {
        score -= 1.0;
    }

    score.min(10.0).max(0.0)
}

// Priority calculation (determines queue order)
fn calculate_priority(parent_score: f32, repo_pre_score: f32, stars: u32) -> f32 {
    // Weighted combination:
    // - 50% parent score (inheritance from successful branch)
    // - 40% pre-score of this repo
    // - 10% star count (weak signal)

    let parent_weight = 0.5;
    let repo_weight = 0.4;
    let star_weight = 0.1;

    parent_score * parent_weight
        + repo_pre_score * repo_weight
        + (stars as f32).log10().min(3.0) * star_weight
}
```

### Traversal Strategies

#### Strategy 1: Depth-First Success Path (DFS)
**When to use:** Deep exploration of high-value branches
**Pros:** Finds clusters of related high-value repos
**Cons:** Can get stuck in one area

```rust
// DFS: Use stack instead of priority queue
let mut stack = Vec::new();
stack.push(seed_repo);

while let Some(repo) = stack.pop() {
    // Process repo...

    // Push children to stack (LIFO)
    for child in discover_related_repos(repo) {
        if score(child) > THRESHOLD {
            stack.push(child); // Explore depth first
        }
    }
}
```

#### Strategy 2: Breadth-First Coverage (BFS)
**When to use:** Wide discovery across many categories
**Pros:** Better coverage, less bias
**Cons:** Slower to find clusters

```rust
// BFS: Use queue instead of stack
let mut queue = VecDeque::new();
queue.push_back(seed_repo);

while let Some(repo) = queue.pop_front() {
    // Process repo...

    // Push children to queue (FIFO)
    for child in discover_related_repos(repo) {
        if score(child) > THRESHOLD {
            queue.push_back(child); // Explore breadth first
        }
    }
}
```

#### Strategy 3: Priority-Based Best-First (Recommended)
**When to use:** Optimal balance of depth and breadth
**Pros:** Always explores most promising paths first
**Cons:** Slightly more complex

```rust
// Best-First: Use priority queue (max heap)
let mut pq = BinaryHeap::new();
pq.push(Reverse((10.0, seed_repo))); // Max priority

while let Some(Reverse((priority, repo))) = pq.pop() {
    // Process highest-priority repo first...

    // Push children with calculated priorities
    for child in discover_related_repos(repo) {
        let child_priority = calculate_priority(repo, child);
        if child_priority > THRESHOLD {
            pq.push(Reverse((child_priority, child)));
        }
    }
}
```

**Recommended:** Strategy 3 (Priority-Based) with adaptive threshold tuning.

### Cycle Detection & Pruning

```rust
// Visited set: Exact membership (HashSet)
let mut visited = HashSet::new();

// Bloom filter: Probabilistic membership (space-efficient)
// - 1M capacity
// - 1% false positive rate
// - ~1.2MB memory (vs ~32MB for HashSet)
let mut bloom = BloomFilter::new(1_000_000, 0.01);

// Check before adding to queue
if !visited.contains(&repo_id) && !bloom.contains(&repo_id) {
    visited.insert(repo_id.clone());
    bloom.insert(&repo_id);
    queue.push(repo_id);
}

// Pruning strategies:
// 1. Score-based pruning (low-value branches)
if score < PRUNE_THRESHOLD {
    continue; // Don't explore children
}

// 2. Depth-based pruning (limit recursion depth)
if depth > MAX_DEPTH {
    continue;
}

// 3. Time-based pruning (limit exploration per seed)
if elapsed_time > MAX_TIME_PER_SEED {
    break;
}

// 4. Rate-limit-based pruning (respect GitHub API limits)
if rate_limit.remaining() < MINIMUM_BUFFER {
    sleep_until_reset().await;
}
```

---

## WASM Module Design

### Rust → WASM Architecture

```
gitbank-wasm/
├── Cargo.toml
├── src/
│   ├── lib.rs                 # WASM entry point
│   ├── graph/
│   │   ├── mod.rs
│   │   ├── traversal.rs       # Graph traversal algorithms
│   │   ├── queue.rs           # Priority queue implementation
│   │   ├── visited.rs         # Visited set + Bloom filter
│   │   └── scoring.rs         # Quick scoring functions
│   ├── github/
│   │   ├── mod.rs
│   │   ├── client.rs          # GitHub API client (async)
│   │   ├── rate_limit.rs      # Rate limit management
│   │   └── cache.rs           # In-memory LRU cache
│   ├── agentdb/
│   │   ├── mod.rs
│   │   ├── embeddings.rs      # Embedding generation
│   │   ├── scoring.rs         # AgentDB-powered scoring
│   │   └── training.rs        # Continuous learning
│   ├── storage/
│   │   ├── mod.rs
│   │   ├── indexeddb.rs       # Browser storage (wasm-bindgen)
│   │   ├── sqlite.rs          # SQLite WASM (for Node.js/CLI)
│   │   └── export.rs          # JSON/CSV export
│   └── utils/
│       ├── mod.rs
│       ├── bloom.rs           # Bloom filter
│       └── metrics.rs         # Performance tracking
└── www/                       # JavaScript bindings
    ├── index.js
    ├── package.json
    └── webpack.config.js
```

### Cargo.toml Configuration

```toml
[package]
name = "gitbank-wasm"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib", "rlib"]

[dependencies]
# WASM bindings
wasm-bindgen = "0.2"
wasm-bindgen-futures = "0.4"
js-sys = "0.3"
web-sys = { version = "0.3", features = [
    "Window",
    "Document",
    "console",
    "IdbDatabase",
    "IdbFactory",
    "IdbTransaction",
    "IdbObjectStore",
] }

# Async runtime (WASM-compatible)
tokio = { version = "1", features = ["sync"], default-features = false }
futures = "0.3"

# HTTP client (WASM-compatible)
reqwest = { version = "0.11", features = ["json"], default-features = false }
gloo-net = "0.4" # Alternative for browser

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Data structures
priority-queue = "1.3"
ahash = "0.8" # Fast hash for WASM
bitvec = "1.0" # For Bloom filter

# Error handling
anyhow = "1.0"
thiserror = "1.0"

# Logging (WASM-compatible)
tracing = "0.1"
tracing-wasm = "0.2"

# Optional: Real embeddings
# fastembed = { version = "3.0", optional = true }

[dev-dependencies]
wasm-bindgen-test = "0.3"

[profile.release]
opt-level = "z"        # Optimize for size
lto = true             # Link-time optimization
codegen-units = 1      # Better optimization
strip = true           # Strip symbols
```

### WASM API Surface (JavaScript Bindings)

```rust
// src/lib.rs

use wasm_bindgen::prelude::*;
use std::sync::Arc;
use tokio::sync::Mutex;

#[wasm_bindgen]
pub struct DiscoveryEngine {
    inner: Arc<Mutex<EngineState>>,
}

#[wasm_bindgen]
impl DiscoveryEngine {
    /// Create a new discovery engine
    #[wasm_bindgen(constructor)]
    pub fn new(github_token: String, agentdb_url: String) -> Result<DiscoveryEngine, JsValue> {
        // Initialize logging for WASM
        tracing_wasm::set_as_global_default();

        let state = EngineState::new(github_token, agentdb_url)
            .map_err(|e| JsValue::from_str(&e.to_string()))?;

        Ok(DiscoveryEngine {
            inner: Arc::new(Mutex::new(state)),
        })
    }

    /// Start discovery from seed repositories
    #[wasm_bindgen]
    pub async fn discover(
        &self,
        seed_repos: Vec<JsValue>,
        max_repos: usize,
        on_progress: js_sys::Function,
    ) -> Result<JsValue, JsValue> {
        let seeds: Vec<String> = seed_repos
            .into_iter()
            .map(|v| v.as_string().unwrap())
            .collect();

        let mut engine = self.inner.lock().await;

        let results = engine.discover_infinite(seeds, max_repos, |progress| {
            // Call JavaScript progress callback
            let this = JsValue::NULL;
            let progress_obj = serde_wasm_bindgen::to_value(&progress).unwrap();
            let _ = on_progress.call1(&this, &progress_obj);
        }).await
            .map_err(|e| JsValue::from_str(&e.to_string()))?;

        // Convert results to JavaScript
        serde_wasm_bindgen::to_value(&results)
            .map_err(|e| JsValue::from_str(&e.to_string()))
    }

    /// Get current statistics
    #[wasm_bindgen]
    pub async fn get_stats(&self) -> Result<JsValue, JsValue> {
        let engine = self.inner.lock().await;
        let stats = engine.get_statistics();

        serde_wasm_bindgen::to_value(&stats)
            .map_err(|e| JsValue::from_str(&e.to_string()))
    }

    /// Export discovered repos to JSON
    #[wasm_bindgen]
    pub async fn export_json(&self) -> Result<String, JsValue> {
        let engine = self.inner.lock().await;
        engine.export_to_json()
            .map_err(|e| JsValue::from_str(&e.to_string()))
    }

    /// Pause discovery
    #[wasm_bindgen]
    pub async fn pause(&self) {
        let mut engine = self.inner.lock().await;
        engine.pause();
    }

    /// Resume discovery
    #[wasm_bindgen]
    pub async fn resume(&self) {
        let mut engine = self.inner.lock().await;
        engine.resume();
    }

    /// Stop discovery
    #[wasm_bindgen]
    pub async fn stop(&self) {
        let mut engine = self.inner.lock().await;
        engine.stop();
    }
}

// Internal state (not exposed to JavaScript)
struct EngineState {
    github: GitHubClient,
    agentdb: AgentDBClient,
    storage: Storage,
    visited: HashSet<String>,
    bloom: BloomFilter,
    paused: bool,
    stopped: bool,
}
```

### JavaScript Usage Example

```javascript
import init, { DiscoveryEngine } from './pkg/gitbank_wasm.js';

// Initialize WASM module
await init();

// Create discovery engine
const engine = new DiscoveryEngine(
    'ghp_YOUR_GITHUB_TOKEN',
    'http://localhost:8765' // AgentDB URL
);

// Start discovery with progress callback
const results = await engine.discover(
    ['eosphoros-ai/DB-GPT'], // Seed repos
    10000, // Max repos to discover
    (progress) => {
        console.log(`Discovered: ${progress.total_discovered}`);
        console.log(`High-value: ${progress.high_value_count}`);
        console.log(`Queue size: ${progress.queue_size}`);
        console.log(`API calls: ${progress.api_calls}`);
    }
);

console.log('Discovery complete!');
console.log(`Total repos: ${results.length}`);

// Export to JSON
const json = await engine.export_json();
console.log(json);

// Get statistics
const stats = await engine.get_stats();
console.log(stats);
```

### WASM Module Size Optimization

```bash
# Build for production
cargo build --target wasm32-unknown-unknown --release

# Optimize with wasm-opt (from binaryen)
wasm-opt -Oz -o pkg/gitbank_wasm_bg.wasm \
    target/wasm32-unknown-unknown/release/gitbank_wasm.wasm

# Expected sizes:
# - Unoptimized: ~1.5MB
# - Optimized: ~500KB
# - Gzipped: ~150KB
```

---

## AgentDB Integration

### Continuous Learning Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│              CONTINUOUS LEARNING LOOP                        │
└─────────────────────────────────────────────────────────────┘

Discovery Phase                 Scoring Phase                Training Phase
─────────────────              ─────────────────            ─────────────────

New Repo Found                 Generate Embedding           Store in AgentDB
      │                              │                             │
      ▼                              ▼                             ▼
Extract Features  ────────►   Search Similar    ────────►   Update Vectors
(name, desc,                  (top-k=10)                   (incremental)
 lang, stars)                       │                             │
      │                              ▼                             ▼
      │                        Calculate Score            Refine Patterns
      │                        (weighted avg)             (background)
      │                              │                             │
      └──────────────────────────────┴─────────────────────────────┘
                                      │
                                      ▼
                    If score >= threshold → Store Opportunity
                    If score < threshold → Prune Branch
```

### AgentDB Client (WASM-Compatible)

```rust
// src/agentdb/mod.rs

use reqwest::Client;
use serde::{Deserialize, Serialize};

pub struct AgentDBClient {
    client: Client,
    base_url: String,
    cache: LruCache<String, Vec<f32>>, // Embedding cache
}

impl AgentDBClient {
    pub fn new(base_url: String) -> Self {
        Self {
            client: Client::new(),
            base_url,
            cache: LruCache::new(1000),
        }
    }

    /// Score a repository based on similarity to known successes
    pub async fn score_repository(&self, repo: &Repository) -> Result<f32> {
        // Generate or retrieve cached embedding
        let embedding = self.get_or_generate_embedding(repo).await?;

        // Search for similar successful repos
        let similar = self.search_similar(embedding, 10).await?;

        // Weighted scoring
        let mut score = 0.0;
        let mut total_weight = 0.0;

        for result in similar {
            let similarity = result.score;
            let revenue_score = result.metadata["revenue_score"]
                .as_f64()
                .unwrap_or(5.0) as f32;

            score += similarity * revenue_score;
            total_weight += similarity;
        }

        if total_weight > 0.0 {
            score /= total_weight;
        } else {
            score = 5.0; // Default score
        }

        // Apply repo quality multiplier
        score *= self.calculate_quality_multiplier(repo);

        Ok(score.min(10.0).max(0.0))
    }

    /// Incremental training (add new discovery to knowledge base)
    pub async fn train_incremental(&self, repo: &Repository, score: f32) -> Result<()> {
        let embedding = self.generate_embedding(repo).await?;

        let metadata = serde_json::json!({
            "name": repo.name,
            "owner": repo.owner,
            "stars": repo.stars,
            "language": repo.language,
            "category": self.classify_category(repo),
            "revenue_score": score,
            "discovered_at": chrono::Utc::now().to_rfc3339(),
        });

        self.store_vector(&format!("{}/{}", repo.owner, repo.name), embedding, metadata)
            .await?;

        Ok(())
    }

    /// Generate embedding for repository
    async fn generate_embedding(&self, repo: &Repository) -> Result<Vec<f32>> {
        // Check cache first
        let cache_key = format!("{}/{}", repo.owner, repo.name);
        if let Some(cached) = self.cache.get(&cache_key) {
            return Ok(cached.clone());
        }

        // Generate new embedding
        let text = format!(
            "{} {} {} {}",
            repo.name,
            repo.description.as_deref().unwrap_or(""),
            repo.language.as_deref().unwrap_or(""),
            repo.topics.join(" ")
        );

        let embedding = generate_simple_embedding(&text);

        // Cache it
        self.cache.put(cache_key, embedding.clone());

        Ok(embedding)
    }

    /// Calculate quality multiplier based on repo characteristics
    fn calculate_quality_multiplier(&self, repo: &Repository) -> f32 {
        let mut multiplier = 1.0;

        // Active maintenance (updated recently)
        if repo.days_since_update() < 90 {
            multiplier *= 1.2;
        } else if repo.days_since_update() > 365 {
            multiplier *= 0.7;
        }

        // Star count (logarithmic bonus)
        if repo.stars > 1000 {
            multiplier *= 1.1;
        }
        if repo.stars > 5000 {
            multiplier *= 1.2;
        }

        // Fork ratio (too high = not original)
        let fork_ratio = repo.forks as f32 / repo.stars.max(1) as f32;
        if fork_ratio > 0.5 {
            multiplier *= 0.8;
        }

        // Has documentation
        if repo.has_wiki || repo.has_readme {
            multiplier *= 1.1;
        }

        // Commercial keywords
        if has_commercial_keywords(&repo.description.as_deref().unwrap_or("")) {
            multiplier *= 1.3;
        }

        multiplier
    }
}
```

### Pattern Extraction & Improvement

```rust
// Periodically extract patterns from discovered repos
pub async fn extract_and_refine_patterns(agentdb: &AgentDBClient) -> Result<()> {
    // Get all high-scoring discoveries
    let high_value_repos = agentdb.query_by_score(8.0, 10.0, limit=100).await?;

    // Analyze common patterns
    let patterns = analyze_patterns(&high_value_repos);

    // Update scoring weights based on patterns
    agentdb.update_scoring_weights(patterns).await?;

    Ok(())
}

fn analyze_patterns(repos: &[Repository]) -> PatternWeights {
    let mut patterns = PatternWeights::default();

    // Language distribution
    let mut lang_counts = HashMap::new();
    for repo in repos {
        *lang_counts.entry(&repo.language).or_insert(0) += 1;
    }
    patterns.language_weights = normalize_weights(lang_counts);

    // Category distribution
    let mut cat_counts = HashMap::new();
    for repo in repos {
        *cat_counts.entry(classify_category(repo)).or_insert(0) += 1;
    }
    patterns.category_weights = normalize_weights(cat_counts);

    // Keyword frequency
    let mut keyword_counts = HashMap::new();
    for repo in repos {
        for keyword in extract_keywords(&repo.description) {
            *keyword_counts.entry(keyword).or_insert(0) += 1;
        }
    }
    patterns.keyword_weights = normalize_weights(keyword_counts);

    patterns
}
```

### AgentDB Training Performance

**Initial Training:**
- 50 opportunities from `detailed_opportunities.json`
- ~1-2 minutes to generate embeddings & store
- Baseline accuracy: 60-70%

**Continuous Learning:**
- Add 1 new discovery per API call
- ~50ms overhead per discovery
- Accuracy improvement: +1-2% per 100 discoveries
- Target accuracy after 500 discoveries: 80-85%

**Vector Search Performance:**
- HNSW index: O(log N) search
- 10K vectors: ~5-10ms per search
- 100K vectors: ~10-20ms per search
- 1M vectors: ~20-50ms per search

---

## Data Flow Pipeline

### End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                       DATA FLOW PIPELINE                             │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Seed Initialization
───────────────────────────
User provides seed repos → Queue initialization
Example: ['eosphoros-ai/DB-GPT']

                ▼

Step 2: GitHub API Fetching
───────────────────────────
Fetch repo details → Fetch stargazers → Fetch user repos
Rate limit: 5000/hour → Cache: 1-hour TTL

                ▼

Step 3: Quick Pre-Filtering
───────────────────────────
Calculate pre-score → Filter by threshold (>= 6.0)
Purpose: Reduce AgentDB calls (expensive)

                ▼

Step 4: AgentDB Scoring
───────────────────────────
Generate embedding → Search similar → Calculate weighted score
Time: ~50-100ms per repo

                ▼

Step 5: Decision Making
───────────────────────────
If score >= 8.0: Store as opportunity
If score >= 6.0: Add children to queue (explore branch)
If score < 6.0: Prune branch (stop recursion)

                ▼

Step 6: Storage
───────────────────────────
IndexedDB (browser) or SQLite (Node.js)
Schema: repos, edges, scores, metadata

                ▼

Step 7: Continuous Training
───────────────────────────
Store in AgentDB → Update patterns → Refine weights
Frequency: Every 100 discoveries

                ▼

Step 8: Export & Reporting
───────────────────────────
JSON export → CSV export → Real-time dashboard
Output: Top opportunities, statistics, graph visualization
```

### Rate Limit Management

```rust
pub struct RateLimiter {
    remaining: Arc<Mutex<usize>>,
    reset_at: Arc<Mutex<Instant>>,
    tokens: Vec<String>,
    current_token_idx: Arc<Mutex<usize>>,
}

impl RateLimiter {
    pub fn new(tokens: Vec<String>) -> Self {
        Self {
            remaining: Arc::new(Mutex::new(5000)),
            reset_at: Arc::new(Mutex::new(Instant::now() + Duration::from_secs(3600))),
            tokens,
            current_token_idx: Arc::new(Mutex::new(0)),
        }
    }

    pub async fn wait_if_needed(&self) {
        let mut remaining = self.remaining.lock().await;
        let reset_at = self.reset_at.lock().await;

        if *remaining < 100 {
            // Try rotating to next token
            if self.try_rotate_token().await {
                *remaining = 5000; // Reset counter
                return;
            }

            // No tokens available, wait for reset
            let wait_time = reset_at.saturating_duration_since(Instant::now());
            if wait_time > Duration::from_secs(0) {
                tracing::warn!("Rate limit exhausted, waiting {} seconds", wait_time.as_secs());
                tokio::time::sleep(wait_time).await;
            }

            *remaining = 5000; // Reset after wait
        }

        *remaining -= 1;
    }

    async fn try_rotate_token(&self) -> bool {
        let mut idx = self.current_token_idx.lock().await;
        if *idx + 1 < self.tokens.len() {
            *idx += 1;
            tracing::info!("Rotated to token #{}", *idx + 1);
            true
        } else {
            false
        }
    }

    pub fn get_current_token(&self) -> String {
        let idx = self.current_token_idx.blocking_lock();
        self.tokens[*idx].clone()
    }
}

// Usage in GitHub client
impl GitHubClient {
    pub async fn get_repo(&self, repo_id: &str) -> Result<Repository> {
        self.rate_limiter.wait_if_needed().await;

        let token = self.rate_limiter.get_current_token();
        let response = self.client
            .get(&format!("https://api.github.com/repos/{}", repo_id))
            .header("Authorization", format!("Bearer {}", token))
            .send()
            .await?;

        // Update rate limit from headers
        if let Some(remaining) = response.headers().get("x-ratelimit-remaining") {
            if let Ok(count) = remaining.to_str().unwrap().parse::<usize>() {
                *self.rate_limiter.remaining.lock().await = count;
            }
        }

        Ok(response.json().await?)
    }
}
```

### Caching Strategy

```rust
pub struct CacheLayer {
    // LRU cache for repo details (1-hour TTL)
    repos: LruCache<String, (Repository, Instant)>,

    // LRU cache for stargazers (1-hour TTL)
    stargazers: LruCache<String, (Vec<User>, Instant)>,

    // LRU cache for user repos (30-min TTL)
    user_repos: LruCache<String, (Vec<Repository>, Instant)>,
}

impl CacheLayer {
    pub fn get_repo(&mut self, repo_id: &str) -> Option<Repository> {
        if let Some((repo, cached_at)) = self.repos.get(repo_id) {
            if cached_at.elapsed() < Duration::from_secs(3600) {
                return Some(repo.clone());
            }
        }
        None
    }

    pub fn put_repo(&mut self, repo_id: String, repo: Repository) {
        self.repos.put(repo_id, (repo, Instant::now()));
    }
}

// Cache hit rate impact on rate limits:
// - Without cache: 5000 repos/hour (1 API call per repo)
// - With 50% cache hit: 10000 repos/hour
// - With 80% cache hit: 25000 repos/hour
```

---

## Deployment Strategy

### Option 1: Browser Extension (Recommended)

**Pros:**
- Distributed execution (crowdsourced)
- No server costs
- User's GitHub token (personal rate limit)
- Easy distribution (Chrome Web Store)

**Cons:**
- Limited by browser resources
- User must keep browser open
- Complex state management

**Architecture:**

```
Chrome Extension Structure:
├── manifest.json
├── background.js          # Service worker (runs WASM engine)
├── popup/
│   ├── index.html         # Control panel
│   ├── popup.js           # UI logic
│   └── styles.css
├── content/
│   └── github_inject.js   # Inject discovery button on GitHub pages
├── wasm/
│   ├── gitbank_wasm.js
│   └── gitbank_wasm_bg.wasm
└── options/
    └── options.html       # Settings (GitHub token, AgentDB URL)
```

**manifest.json:**

```json
{
  "manifest_version": 3,
  "name": "GitBank Discovery Engine",
  "version": "1.0.0",
  "description": "Infinite repository discovery through social graphs",
  "permissions": [
    "storage",
    "unlimitedStorage",
    "alarms"
  ],
  "host_permissions": [
    "https://api.github.com/*",
    "http://localhost:8765/*"
  ],
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "action": {
    "default_popup": "popup/index.html",
    "default_icon": "icons/icon128.png"
  },
  "content_scripts": [
    {
      "matches": ["https://github.com/*/*"],
      "js": ["content/github_inject.js"]
    }
  ],
  "web_accessible_resources": [
    {
      "resources": ["wasm/*"],
      "matches": ["<all_urls>"]
    }
  ]
}
```

**background.js (Service Worker):**

```javascript
import init, { DiscoveryEngine } from './wasm/gitbank_wasm.js';

let engine = null;
let discoveryState = 'stopped'; // stopped, running, paused

// Initialize WASM module
init().then(() => {
  console.log('WASM module initialized');
});

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'start_discovery') {
    startDiscovery(request.seeds, request.maxRepos);
    sendResponse({ status: 'started' });
  } else if (request.action === 'stop_discovery') {
    stopDiscovery();
    sendResponse({ status: 'stopped' });
  } else if (request.action === 'get_stats') {
    getStats().then(stats => sendResponse(stats));
    return true; // Keep channel open for async response
  }
});

async function startDiscovery(seeds, maxRepos) {
  // Get GitHub token from storage
  const { githubToken, agentdbUrl } = await chrome.storage.sync.get(['githubToken', 'agentdbUrl']);

  if (!githubToken) {
    console.error('GitHub token not configured');
    return;
  }

  // Create engine
  engine = new DiscoveryEngine(githubToken, agentdbUrl || 'http://localhost:8765');

  discoveryState = 'running';

  // Start discovery with progress callback
  engine.discover(seeds, maxRepos, (progress) => {
    // Send progress to popup
    chrome.runtime.sendMessage({ type: 'progress', data: progress });

    // Store in IndexedDB
    storeProgress(progress);
  }).then(results => {
    discoveryState = 'stopped';
    chrome.runtime.sendMessage({ type: 'complete', data: results });
  }).catch(error => {
    console.error('Discovery error:', error);
    discoveryState = 'stopped';
  });
}

async function stopDiscovery() {
  if (engine) {
    await engine.stop();
    discoveryState = 'stopped';
  }
}

async function getStats() {
  if (engine) {
    return await engine.get_stats();
  }
  return { discovered: 0, high_value: 0 };
}
```

**popup/popup.js:**

```javascript
document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('start');
  const stopBtn = document.getElementById('stop');
  const seedInput = document.getElementById('seeds');
  const statsDiv = document.getElementById('stats');

  // Load saved seeds
  chrome.storage.sync.get(['seeds'], (result) => {
    if (result.seeds) {
      seedInput.value = result.seeds.join('\n');
    }
  });

  startBtn.addEventListener('click', () => {
    const seeds = seedInput.value.split('\n').filter(s => s.trim());
    chrome.storage.sync.set({ seeds });

    chrome.runtime.sendMessage({
      action: 'start_discovery',
      seeds,
      maxRepos: 10000
    }, (response) => {
      console.log('Discovery started:', response);
    });
  });

  stopBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'stop_discovery' }, (response) => {
      console.log('Discovery stopped:', response);
    });
  });

  // Listen for progress updates
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'progress') {
      updateStats(request.data);
    } else if (request.type === 'complete') {
      showComplete(request.data);
    }
  });

  // Poll for stats every 2 seconds
  setInterval(() => {
    chrome.runtime.sendMessage({ action: 'get_stats' }, (stats) => {
      updateStats(stats);
    });
  }, 2000);
});

function updateStats(stats) {
  document.getElementById('stats').innerHTML = `
    <div>Discovered: ${stats.total_discovered}</div>
    <div>High-value: ${stats.high_value_count}</div>
    <div>Queue size: ${stats.queue_size}</div>
    <div>API calls: ${stats.api_calls}</div>
  `;
}
```

### Option 2: Node.js CLI Tool

**Pros:**
- Full system resources
- Can run 24/7 on server
- Better performance than browser
- Easier debugging

**Cons:**
- Requires Node.js runtime
- Single-instance (not distributed)
- Server costs for 24/7 operation

**Installation:**

```bash
npm install -g gitbank-discovery
gitbank-discovery --version
```

**Usage:**

```bash
# Start discovery
gitbank-discovery discover \
  --seeds "eosphoros-ai/DB-GPT,FunnyWolf/Viper" \
  --token $GITHUB_TOKEN \
  --agentdb http://localhost:8765 \
  --max-repos 10000 \
  --output discoveries.json

# Resume from checkpoint
gitbank-discovery resume \
  --checkpoint discoveries.checkpoint.json

# Export results
gitbank-discovery export \
  --input discoveries.json \
  --format csv \
  --output discoveries.csv

# View statistics
gitbank-discovery stats \
  --input discoveries.json
```

### Option 3: Rust CLI (Native Binary)

**Pros:**
- Best performance (native)
- No runtime dependencies
- Single-file binary
- Cross-platform

**Cons:**
- Larger binary size
- Harder to distribute
- WASM not used (native code)

**Build:**

```bash
cd gitbank-rust
cargo build --release --bin gitbank-discovery
```

**Usage:**

```bash
# Start discovery
./target/release/gitbank-discovery discover \
  --seeds "eosphoros-ai/DB-GPT,FunnyWolf/Viper" \
  --token $GITHUB_TOKEN \
  --agentdb http://localhost:8765 \
  --max-repos 10000 \
  --output discoveries.json

# Real-time monitoring
./target/release/gitbank-discovery discover \
  --seeds "eosphoros-ai/DB-GPT" \
  --monitor \
  --dashboard http://localhost:3000
```

### Option 4: Web Service (Cloud Deployment)

**Pros:**
- Always running
- Multi-user support
- Centralized database
- Easy access (web UI)

**Cons:**
- Highest cost
- Rate limits shared
- Privacy concerns (tokens)

**Architecture:**

```
Cloud Service:
├── Frontend (React)
│   └── Dashboard, controls, visualization
├── Backend (Rust/Axum)
│   ├── Discovery API
│   ├── Job queue (Tokio tasks)
│   └── WebSocket (real-time updates)
├── WASM Worker Pool
│   └── 10+ parallel discovery instances
├── PostgreSQL
│   └── Discoveries, users, jobs
└── Redis
    └── Cache, job queue
```

---

## Performance Optimization

### Expected Performance Metrics

**Discovery Rate:**
- Without cache: 5,000 repos/hour (rate limit bound)
- With 50% cache: 10,000 repos/hour
- With 80% cache: 25,000 repos/hour
- Multiple tokens: N × base rate

**Pattern Accuracy:**
- Initial (50 seeds): 60-70%
- After 500 discoveries: 75-80%
- After 2000 discoveries: 80-85%
- Ceiling: ~85% (inherent uncertainty)

**Resource Usage:**
- WASM module: ~500KB (compressed)
- Memory: 50-100MB (browser), 100-500MB (Node.js)
- CPU: 10-20% (single core)
- Network: 100-500 KB/s (API calls)

### Optimization Strategies

#### 1. Parallel Discovery (Multiple Instances)

```rust
// Run multiple discovery instances with different seeds
pub async fn parallel_discover(
    seeds: Vec<String>,
    num_instances: usize,
) -> Result<Vec<Repository>> {
    let chunks = seeds.chunks(seeds.len() / num_instances);

    let handles: Vec<_> = chunks.enumerate().map(|(i, chunk)| {
        let chunk_seeds = chunk.to_vec();
        tokio::spawn(async move {
            let engine = DiscoveryEngine::new(
                get_token(i), // Rotate tokens
                AGENTDB_URL.to_string()
            ).await?;

            engine.discover(chunk_seeds, MAX_REPOS_PER_INSTANCE).await
        })
    }).collect();

    let results = futures::future::try_join_all(handles).await?;

    // Merge and deduplicate
    let merged = merge_results(results);

    Ok(merged)
}

// Expected speedup:
// - 1 instance: 5,000 repos/hour
// - 4 instances: 20,000 repos/hour
// - 10 instances: 50,000 repos/hour
```

#### 2. Aggressive Caching

```rust
pub struct MultiLayerCache {
    // L1: In-memory LRU (fast, small)
    l1: LruCache<String, Repository>,

    // L2: IndexedDB/SQLite (medium, larger)
    l2: Box<dyn StorageBackend>,

    // L3: AgentDB vector search (slow, semantic)
    l3: AgentDBClient,
}

impl MultiLayerCache {
    pub async fn get_repo(&mut self, repo_id: &str) -> Result<Option<Repository>> {
        // Try L1 (fastest)
        if let Some(repo) = self.l1.get(repo_id) {
            return Ok(Some(repo.clone()));
        }

        // Try L2 (medium)
        if let Some(repo) = self.l2.get(repo_id).await? {
            self.l1.put(repo_id.to_string(), repo.clone());
            return Ok(Some(repo));
        }

        // Try L3 (semantic search)
        if let Some(repo) = self.l3.find_similar(repo_id).await? {
            self.l1.put(repo_id.to_string(), repo.clone());
            self.l2.put(repo_id, &repo).await?;
            return Ok(Some(repo));
        }

        // Cache miss
        Ok(None)
    }
}

// Cache hit rates:
// - L1: ~30% (10K capacity)
// - L2: ~50% (100K capacity)
// - L3: ~10% (semantic matches)
// - Total: ~90% cache hits
```

#### 3. Batch API Requests

```rust
// Instead of 1 repo per request, batch multiple repos
pub async fn batch_get_repos(&self, repo_ids: &[String]) -> Result<Vec<Repository>> {
    // GitHub GraphQL API supports batching
    let query = format!(r#"
        query {{
            {}
        }}
    "#, repo_ids.iter().enumerate().map(|(i, id)| {
        format!("repo{}: repository(owner: \"{}\", name: \"{}\") {{ ... }}",
            i, id.split('/').nth(0).unwrap(), id.split('/').nth(1).unwrap())
    }).collect::<Vec<_>>().join("\n"));

    let response = self.client
        .post("https://api.github.com/graphql")
        .json(&serde_json::json!({ "query": query }))
        .send()
        .await?;

    // Parse batched results
    let repos = parse_batch_response(response).await?;

    Ok(repos)
}

// Speedup:
// - Single request: 1 repo per API call
// - Batched request: 50 repos per API call
// - 50x reduction in API calls
```

#### 4. Smart Pruning

```rust
pub fn should_prune_branch(&self, repo: &Repository, depth: usize) -> bool {
    // Prune if:

    // 1. Low score
    if repo.score < PRUNE_THRESHOLD {
        return true;
    }

    // 2. Too deep
    if depth > MAX_DEPTH {
        return true;
    }

    // 3. Low engagement (stars/forks)
    if repo.stars < 50 && depth > 3 {
        return true;
    }

    // 4. Archived or inactive
    if repo.archived || repo.days_since_update() > 365 {
        return true;
    }

    // 5. Too many forks (not original)
    if repo.forks as f32 / repo.stars.max(1) as f32 > 0.7 {
        return true;
    }

    // 6. Low-value languages (Jupyter Notebook, Makefile)
    if LOW_VALUE_LANGUAGES.contains(&repo.language.as_str()) {
        return true;
    }

    false
}

// Pruning effectiveness:
// - Without pruning: 100K repos explored, 1K high-value
// - With pruning: 10K repos explored, 950 high-value
// - 10x efficiency gain, 5% accuracy loss
```

---

## Storage Strategy

### Browser: IndexedDB

```javascript
// IndexedDB schema
const DB_NAME = 'gitbank-discovery';
const DB_VERSION = 1;

const schema = {
  repos: {
    keyPath: 'id',
    indexes: [
      { name: 'score', keyPath: 'score' },
      { name: 'stars', keyPath: 'stars' },
      { name: 'language', keyPath: 'language' },
      { name: 'discovered_at', keyPath: 'discovered_at' }
    ]
  },
  edges: {
    keyPath: 'id',
    indexes: [
      { name: 'from', keyPath: 'from' },
      { name: 'to', keyPath: 'to' }
    ]
  },
  visited: {
    keyPath: 'repo_id',
    indexes: []
  },
  checkpoints: {
    keyPath: 'timestamp',
    indexes: []
  }
};

// Usage
class IndexedDBStorage {
  async open() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Create object stores
        const reposStore = db.createObjectStore('repos', { keyPath: 'id' });
        reposStore.createIndex('score', 'score');
        reposStore.createIndex('stars', 'stars');
        // ... more indexes
      };
    });
  }

  async storeRepo(repo) {
    const db = await this.open();
    const tx = db.transaction(['repos'], 'readwrite');
    const store = tx.objectStore('repos');
    await store.put(repo);
  }

  async getHighValueRepos(minScore = 8.0) {
    const db = await this.open();
    const tx = db.transaction(['repos'], 'readonly');
    const store = tx.objectStore('repos');
    const index = store.index('score');

    const range = IDBKeyRange.lowerBound(minScore);
    const repos = [];

    return new Promise((resolve) => {
      const cursor = index.openCursor(range, 'prev');
      cursor.onsuccess = (event) => {
        const cursor = event.target.result;
        if (cursor) {
          repos.push(cursor.value);
          cursor.continue();
        } else {
          resolve(repos);
        }
      };
    });
  }
}
```

### Node.js: SQLite WASM

```rust
// Using rusqlite with WASM compilation
pub struct SQLiteStorage {
    conn: Connection,
}

impl SQLiteStorage {
    pub fn new(db_path: &str) -> Result<Self> {
        let conn = Connection::open(db_path)?;

        // Create schema
        conn.execute_batch(r#"
            CREATE TABLE IF NOT EXISTS repos (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                owner TEXT NOT NULL,
                description TEXT,
                stars INTEGER,
                forks INTEGER,
                language TEXT,
                category TEXT,
                score REAL,
                discovered_at TEXT,
                metadata TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_score ON repos(score);
            CREATE INDEX IF NOT EXISTS idx_stars ON repos(stars);
            CREATE INDEX IF NOT EXISTS idx_language ON repos(language);

            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_repo TEXT NOT NULL,
                to_repo TEXT NOT NULL,
                via_user TEXT,
                discovered_at TEXT,
                UNIQUE(from_repo, to_repo)
            );

            CREATE INDEX IF NOT EXISTS idx_edges_from ON edges(from_repo);
            CREATE INDEX IF NOT EXISTS idx_edges_to ON edges(to_repo);

            CREATE TABLE IF NOT EXISTS visited (
                repo_id TEXT PRIMARY KEY,
                visited_at TEXT
            );

            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                state TEXT,
                stats TEXT
            );
        "#)?;

        Ok(Self { conn })
    }

    pub fn store_repo(&self, repo: &Repository, score: f32) -> Result<()> {
        self.conn.execute(
            r#"
            INSERT OR REPLACE INTO repos
            (id, name, owner, description, stars, forks, language, category, score, discovered_at, metadata)
            VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)
            "#,
            params![
                repo.id,
                repo.name,
                repo.owner,
                repo.description,
                repo.stars,
                repo.forks,
                repo.language,
                repo.category,
                score,
                chrono::Utc::now().to_rfc3339(),
                serde_json::to_string(&repo.metadata)?
            ]
        )?;

        Ok(())
    }

    pub fn get_high_value_repos(&self, min_score: f32, limit: usize) -> Result<Vec<Repository>> {
        let mut stmt = self.conn.prepare(
            "SELECT * FROM repos WHERE score >= ?1 ORDER BY score DESC LIMIT ?2"
        )?;

        let repos = stmt.query_map(params![min_score, limit], |row| {
            Ok(Repository {
                id: row.get(0)?,
                name: row.get(1)?,
                owner: row.get(2)?,
                description: row.get(3)?,
                stars: row.get(4)?,
                forks: row.get(5)?,
                language: row.get(6)?,
                category: row.get(7)?,
                // ... more fields
            })
        })?.collect::<Result<Vec<_>, _>>()?;

        Ok(repos)
    }
}
```

### Checkpoint & Resume

```rust
pub struct Checkpoint {
    timestamp: String,
    queue: Vec<(f32, String)>,
    visited: HashSet<String>,
    stats: Statistics,
}

impl DiscoveryEngine {
    pub async fn save_checkpoint(&self) -> Result<()> {
        let checkpoint = Checkpoint {
            timestamp: chrono::Utc::now().to_rfc3339(),
            queue: self.queue.iter().cloned().collect(),
            visited: self.visited.clone(),
            stats: self.stats.clone(),
        };

        let json = serde_json::to_string(&checkpoint)?;
        self.storage.save_checkpoint(&json).await?;

        Ok(())
    }

    pub async fn load_checkpoint(checkpoint_data: &str) -> Result<Self> {
        let checkpoint: Checkpoint = serde_json::from_str(checkpoint_data)?;

        let mut engine = Self::new(/* ... */);
        engine.queue = checkpoint.queue.into_iter().collect();
        engine.visited = checkpoint.visited;
        engine.stats = checkpoint.stats;

        Ok(engine)
    }
}

// Auto-save every 5 minutes
async fn auto_checkpoint_loop(engine: Arc<Mutex<DiscoveryEngine>>) {
    let mut interval = tokio::time::interval(Duration::from_secs(300));

    loop {
        interval.tick().await;

        let engine = engine.lock().await;
        if let Err(e) = engine.save_checkpoint().await {
            tracing::warn!("Failed to save checkpoint: {}", e);
        } else {
            tracing::info!("Checkpoint saved");
        }
    }
}
```

---

## Implementation Roadmap

### Phase 1: Core WASM Module (Weeks 1-2)

**Deliverables:**
- [ ] Rust project setup (`gitbank-wasm/`)
- [ ] Basic graph traversal (BFS/DFS)
- [ ] Priority queue implementation
- [ ] Visited set + Bloom filter
- [ ] GitHub API client (WASM-compatible)
- [ ] Rate limiter
- [ ] WASM bindings (wasm-bindgen)
- [ ] JavaScript API

**Testing:**
- Unit tests for graph algorithms
- Integration tests with mock GitHub API
- Performance benchmarks

**Success Criteria:**
- WASM module compiles (<1MB)
- Can traverse 1000 repos in <1 minute
- Rate limiter works correctly

### Phase 2: AgentDB Integration (Weeks 3-4)

**Deliverables:**
- [ ] AgentDB client (WASM-compatible)
- [ ] Embedding generation (simple)
- [ ] Vector search integration
- [ ] Scoring algorithm
- [ ] Continuous learning pipeline
- [ ] Pattern extraction

**Testing:**
- Train on existing 50 opportunities
- Test similarity search accuracy
- Benchmark scoring performance

**Success Criteria:**
- AgentDB training works (50 opportunities)
- Scoring accuracy > 70%
- <100ms per score

### Phase 3: Storage & Checkpoints (Week 5)

**Deliverables:**
- [ ] IndexedDB backend (browser)
- [ ] SQLite WASM backend (Node.js)
- [ ] Checkpoint/resume functionality
- [ ] Export to JSON/CSV

**Testing:**
- Store/retrieve 10K repos
- Test checkpoint recovery
- Test export formats

**Success Criteria:**
- Can store 100K+ repos
- Checkpoint recovery works
- Export formats valid

### Phase 4: Browser Extension (Week 6)

**Deliverables:**
- [ ] Chrome extension manifest
- [ ] Background service worker
- [ ] Popup UI (control panel)
- [ ] Content script (GitHub injection)
- [ ] Settings page

**Testing:**
- Test in Chrome/Edge/Firefox
- Test with multiple tabs
- Test suspend/resume

**Success Criteria:**
- Extension installs correctly
- Discovery runs in background
- UI updates in real-time

### Phase 5: Node.js CLI (Week 7)

**Deliverables:**
- [ ] CLI argument parsing (clap)
- [ ] Discover command
- [ ] Resume command
- [ ] Export command
- [ ] Stats command
- [ ] Real-time progress bar

**Testing:**
- Test all commands
- Test error handling
- Test checkpoint recovery

**Success Criteria:**
- CLI works on Linux/Mac/Windows
- Can run for hours without crashes
- Clear progress reporting

### Phase 6: Optimization & Scaling (Week 8)

**Deliverables:**
- [ ] Multi-token rotation
- [ ] Parallel instances
- [ ] Aggressive caching
- [ ] Smart pruning refinement
- [ ] Batch API requests

**Testing:**
- Load testing (100K repos)
- Rate limit testing
- Memory profiling

**Success Criteria:**
- 10K+ repos/hour discovery rate
- <500MB memory usage
- No rate limit violations

### Phase 7: Production Deployment (Week 9-10)

**Deliverables:**
- [ ] Documentation (user guide)
- [ ] Video tutorial
- [ ] Chrome Web Store submission
- [ ] npm package publication
- [ ] GitHub releases (binaries)

**Testing:**
- User acceptance testing
- Beta testing with 10 users
- Bug fixes

**Success Criteria:**
- Extension approved by Chrome Web Store
- npm package published
- Documentation complete

---

## Expected Discovery Rates

### Scenario 1: Single Instance (Browser Extension)

**Setup:**
- 1 GitHub token (5000 req/hour)
- 50% cache hit rate
- Seeds: 5 high-value repos

**Expected Performance:**
- Hour 1: 1,000 repos discovered, 50 high-value (5%)
- Hour 2: 2,500 repos discovered, 150 high-value (6%)
- Hour 4: 5,000 repos discovered, 350 high-value (7%)
- Hour 8: 10,000 repos discovered, 800 high-value (8%)

**Explanation:** Discovery rate accelerates as:
- Cache hits increase (more overlap in graph)
- AgentDB learns patterns (better pruning)
- Fewer low-value branches explored

### Scenario 2: Multiple Instances (10 tokens)

**Setup:**
- 10 GitHub tokens (50K req/hour total)
- 80% cache hit rate (shared cache)
- Seeds: 50 diverse repos

**Expected Performance:**
- Hour 1: 15,000 repos discovered, 1,200 high-value (8%)
- Hour 4: 80,000 repos discovered, 7,200 high-value (9%)
- Hour 8: 200,000 repos discovered, 20,000 high-value (10%)

**Explanation:** Sub-linear scaling due to:
- Overlap between instances
- Shared cache reduces redundant API calls
- Better pattern learning with more data

### Scenario 3: 24/7 Production (Month 1)

**Setup:**
- 20 GitHub tokens (100K req/hour)
- 90% cache hit rate (mature cache)
- Seeds: 100 top repos (updated weekly)

**Expected Performance:**
- Week 1: 500K repos, 50K high-value (10%)
- Week 2: 1.2M repos, 132K high-value (11%)
- Week 4: 3M repos, 360K high-value (12%)
- Month 1 Total: 5-10M repos, 600K-1.2M high-value (12%)

**Revenue Opportunities:**
- If 10% of high-value repos are actionable: 60K-120K opportunities
- If 1% convert to deals: 600-1,200 deals
- At $50K avg revenue per deal: $30M-60M potential

---

## Conclusion

This WASM-based infinite discovery system represents a paradigm shift from static GitHub searches to dynamic graph traversal. By following "success paths" and continuously learning from discoveries, the system creates a self-improving engine that gets smarter over time.

**Key Innovations:**
1. **Graph Traversal:** Explores GitHub's social graph recursively
2. **Success Path Detection:** Only follows branches with high commercial potential
3. **Continuous Learning:** AgentDB improves patterns as it discovers
4. **WASM Performance:** Near-native speed in browser or Node.js
5. **Distributed Execution:** Can run in 1000s of browsers simultaneously

**Next Steps:**
1. Review architecture (this document)
2. Approve implementation plan
3. Begin Phase 1 development (Core WASM module)
4. Parallel: Train AgentDB on existing 50+ opportunities

**Timeline:** 10 weeks to production-ready system

**Investment:** Development time (no infrastructure costs until scaling)

**Expected ROI:** 600-1,200 deals/month × $50K avg = $30M-60M annual potential

---

**Document Status:** Complete ✓
**Ready for Implementation:** Yes
**Risk Level:** Low (incremental development, proven technologies)
**Confidence:** High (based on existing AgentDB + GitHub data)
