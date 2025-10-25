# WASM Discovery System - Quick Reference Card

**One-page reference for developers implementing the system**

---

## System Architecture (Visual)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                         INFINITE DISCOVERY ENGINE                          │
└───────────────────────────────────────────────────────────────────────────┘

┌─────────────┐
│   INPUTS    │
├─────────────┤
│ Seed Repos  │───┐
│ GitHub      │   │
│ Token       │   │
│ AgentDB URL │   │
└─────────────┘   │
                  │
                  ▼
    ┌─────────────────────────────────────────────┐
    │         DISCOVERY STATE MACHINE             │
    ├─────────────────────────────────────────────┤
    │                                             │
    │  ┌──────────────────────────────────┐      │
    │  │ Priority Queue                   │      │
    │  │ (score, repo_id)                 │      │
    │  │ Sorted: Highest score first      │      │
    │  └──────────────────────────────────┘      │
    │                  │                          │
    │                  ▼                          │
    │  ┌──────────────────────────────────┐      │
    │  │ Visited Set + Bloom Filter       │      │
    │  │ Deduplication & Cycle Detection  │      │
    │  └──────────────────────────────────┘      │
    │                  │                          │
    │                  ▼                          │
    │  ┌──────────────────────────────────┐      │
    │  │ Rate Limiter                     │      │
    │  │ 5000 req/hour per token          │      │
    │  │ Multi-token rotation             │      │
    │  └──────────────────────────────────┘      │
    │                                             │
    └─────────────────────────────────────────────┘
                      │
                      ▼
    ┌─────────────────────────────────────────────┐
    │         PROCESSING PIPELINE                 │
    ├─────────────────────────────────────────────┤
    │                                             │
    │  1. Fetch Repo Details (GitHub API)        │
    │     └─► Cache check first (LRU)            │
    │                                             │
    │  2. Quick Pre-Score (Fast Filter)          │
    │     └─► Stars, language, keywords           │
    │                                             │
    │  3. AgentDB Scoring (Expensive)            │
    │     └─► Generate embedding                  │
    │     └─► Search similar (top-k=10)          │
    │     └─► Weighted score calculation         │
    │                                             │
    │  4. Decision Tree                          │
    │     ├─► score >= 8.0: Store as opportunity │
    │     ├─► score >= 6.0: Explore children     │
    │     └─► score < 6.0: Prune branch          │
    │                                             │
    │  5. Graph Expansion                        │
    │     └─► Get stargazers → Get their repos  │
    │     └─► Add to queue with priority         │
    │                                             │
    │  6. Continuous Learning                    │
    │     └─► Train AgentDB on discoveries       │
    │     └─► Update pattern weights             │
    │                                             │
    └─────────────────────────────────────────────┘
                      │
                      ▼
    ┌─────────────────────────────────────────────┐
    │         STORAGE & OUTPUT                    │
    ├─────────────────────────────────────────────┤
    │                                             │
    │  IndexedDB (Browser) / SQLite (Node.js)    │
    │  ├─► Discovered repos                       │
    │  ├─► Graph edges                            │
    │  ├─► Visited set                            │
    │  └─► Checkpoints                            │
    │                                             │
    │  Exports                                    │
    │  ├─► JSON (structured data)                │
    │  ├─► CSV (spreadsheet)                     │
    │  └─► GraphML (visualization)               │
    │                                             │
    └─────────────────────────────────────────────┘
                      │
                      ▼
    ┌─────────────────────────────────────────────┐
    │   OUTPUTS: Discovered Opportunities         │
    └─────────────────────────────────────────────┘
```

---

## Core Algorithm (Pseudocode)

```rust
fn discover_infinite(seeds: Vec<String>) -> Result<Vec<Repository>> {
    // Initialize data structures
    let mut queue = BinaryHeap::new();          // Max-heap: (priority, repo_id)
    let mut visited = HashSet::new();           // Exact membership
    let mut bloom = BloomFilter::new(1M, 0.01); // Probabilistic dedup
    let mut results = Vec::new();               // High-value discoveries

    // Add seeds to queue
    for seed in seeds {
        queue.push((10.0, seed)); // Max priority
    }

    // Main discovery loop
    while let Some((priority, repo_id)) = queue.pop() {
        // Skip if already visited
        if visited.contains(&repo_id) || bloom.contains(&repo_id) {
            continue;
        }

        // Mark as visited
        visited.insert(repo_id.clone());
        bloom.insert(&repo_id);

        // Fetch repo details from GitHub
        let repo = github.get_repo(&repo_id).await?;

        // Score repository
        let score = agentdb.score_repository(&repo).await?;

        // Decision tree
        if score >= 8.0 {
            // High-value: Store as opportunity
            results.push(repo.clone());
            storage.store_repo(&repo, score).await?;

            // Train AgentDB (continuous learning)
            agentdb.train_incremental(&repo, score).await?;
        }

        if score >= 6.0 {
            // Promising: Explore children
            let stargazers = github.get_stargazers(&repo_id).await?;

            for user in stargazers {
                let user_repos = github.get_user_repos(&user.login).await?;

                for child_repo in user_repos {
                    let child_id = format!("{}/{}", child_repo.owner, child_repo.name);

                    // Skip if visited
                    if visited.contains(&child_id) || bloom.contains(&child_id) {
                        continue;
                    }

                    // Quick pre-score (fast filter)
                    let pre_score = quick_score(&child_repo);

                    if pre_score >= 5.0 {
                        // Calculate priority
                        let priority = calculate_priority(score, pre_score, child_repo.stars);

                        // Add to queue
                        queue.push((priority, child_id));
                    }
                }
            }
        } else {
            // Low-value: Prune branch (don't explore children)
            log::info!("Pruning branch: {} (score: {})", repo_id, score);
        }

        // Rate limit check
        rate_limiter.wait_if_needed().await?;

        // Checkpoint every 100 iterations
        if visited.len() % 100 == 0 {
            save_checkpoint(&queue, &visited).await?;
        }
    }

    Ok(results)
}
```

---

## Key Functions

### 1. Score Repository (AgentDB-Powered)

```rust
async fn score_repository(repo: &Repository) -> f32 {
    // Generate embedding
    let embedding = generate_embedding(repo);

    // Search for similar successful repos
    let similar = agentdb.search_similar(embedding, top_k=10).await?;

    // Weighted score
    let mut score = 0.0;
    let mut weight = 0.0;

    for result in similar {
        score += result.score * result.metadata["revenue_score"];
        weight += result.score;
    }

    if weight > 0.0 {
        score /= weight;
    }

    // Apply quality multiplier
    score *= quality_multiplier(repo);

    score.clamp(0.0, 10.0)
}
```

### 2. Quick Pre-Score (Fast Filter)

```rust
fn quick_score(repo: &RepositoryMetadata) -> f32 {
    let mut score = 5.0; // Baseline

    // Star count (logarithmic)
    score += (repo.stars as f32).log10() * 0.5;

    // Language (valuable languages)
    if ["Python", "JavaScript", "Rust", "Go"].contains(&repo.language) {
        score += 1.0;
    }

    // Keywords (commercial indicators)
    if has_keywords(&repo.description, &["API", "SaaS", "enterprise"]) {
        score += 1.0;
    }

    // Recency (active maintenance)
    if repo.updated_within_days(90) {
        score += 0.5;
    }

    // Fork ratio (originality)
    if (repo.forks as f32 / repo.stars.max(1) as f32) > 0.5 {
        score -= 1.0;
    }

    score.clamp(0.0, 10.0)
}
```

### 3. Calculate Priority (Queue Ordering)

```rust
fn calculate_priority(parent_score: f32, repo_score: f32, stars: u32) -> f32 {
    // Weighted combination:
    // 50% parent score (inheritance)
    // 40% repo pre-score
    // 10% star count (weak signal)

    parent_score * 0.5
        + repo_score * 0.4
        + (stars as f32).log10().min(3.0) * 0.1
}
```

### 4. Quality Multiplier (Boost/Penalize)

```rust
fn quality_multiplier(repo: &Repository) -> f32 {
    let mut mult = 1.0;

    // Active maintenance
    if repo.days_since_update() < 90 {
        mult *= 1.2;
    } else if repo.days_since_update() > 365 {
        mult *= 0.7;
    }

    // Star thresholds
    if repo.stars > 1000 { mult *= 1.1; }
    if repo.stars > 5000 { mult *= 1.2; }

    // Fork ratio
    if (repo.forks as f32 / repo.stars.max(1) as f32) > 0.5 {
        mult *= 0.8;
    }

    // Documentation
    if repo.has_readme || repo.has_wiki {
        mult *= 1.1;
    }

    // Commercial keywords
    if has_commercial_keywords(&repo.description) {
        mult *= 1.3;
    }

    mult
}
```

---

## Configuration Constants

```rust
// Scoring thresholds
const SUCCESS_THRESHOLD: f32 = 8.0;    // Store as opportunity
const EXPLORE_THRESHOLD: f32 = 6.0;    // Explore children
const PRUNE_THRESHOLD: f32 = 6.0;      // Stop recursion
const PRE_FILTER_THRESHOLD: f32 = 5.0; // Add to queue

// Traversal limits
const MAX_DEPTH: usize = 10;           // Max recursion depth
const MAX_STARGAZERS: usize = 100;     // Stargazers per repo
const MAX_USER_REPOS: usize = 50;      // Repos per user
const MAX_TIME_PER_SEED: Duration = Duration::from_secs(3600); // 1 hour

// Rate limiting
const RATE_LIMIT_BUFFER: usize = 100;  // Stop before exhaustion
const RATE_LIMIT_RESET: Duration = Duration::from_secs(3600); // 1 hour

// Caching
const CACHE_SIZE_L1: usize = 10_000;   // In-memory LRU
const CACHE_SIZE_L2: usize = 100_000;  // IndexedDB/SQLite
const CACHE_TTL: Duration = Duration::from_secs(3600); // 1 hour

// Bloom filter
const BLOOM_CAPACITY: usize = 1_000_000; // 1M repos
const BLOOM_FP_RATE: f64 = 0.01;        // 1% false positives

// Checkpointing
const CHECKPOINT_INTERVAL: usize = 100;  // Every 100 iterations
const AUTO_SAVE_INTERVAL: Duration = Duration::from_secs(300); // 5 minutes

// AgentDB
const AGENTDB_TOP_K: usize = 10;       // Similar repos to fetch
const EMBEDDING_DIM: usize = 128;       // Embedding dimensions
```

---

## Data Structures

### Repository

```rust
struct Repository {
    id: String,              // "owner/name"
    name: String,
    owner: String,
    description: Option<String>,
    stars: u32,
    forks: u32,
    watchers: u32,
    language: Option<String>,
    topics: Vec<String>,
    has_readme: bool,
    has_wiki: bool,
    archived: bool,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
    pushed_at: DateTime<Utc>,
    homepage: Option<String>,
    license: Option<String>,
}
```

### User

```rust
struct User {
    login: String,
    id: u64,
    name: Option<String>,
    company: Option<String>,
    location: Option<String>,
    email: Option<String>,
    followers: u32,
    following: u32,
    public_repos: u32,
}
```

### Discovery State

```rust
struct DiscoveryState {
    queue: BinaryHeap<(f32, String)>,    // Priority queue
    visited: HashSet<String>,            // Visited repos
    bloom: BloomFilter,                  // Probabilistic dedup
    rate_limiter: RateLimiter,           // API rate limiting
    cache: MultiLayerCache,              // L1, L2, L3 cache
    stats: Statistics,                   // Performance metrics
    paused: bool,
    stopped: bool,
}
```

### Statistics

```rust
struct Statistics {
    total_discovered: usize,
    high_value_count: usize,
    queue_size: usize,
    visited_count: usize,
    api_calls: usize,
    cache_hits: usize,
    cache_misses: usize,
    rate_limit_remaining: usize,
    elapsed_time: Duration,
    repos_per_hour: f32,
}
```

---

## Performance Metrics

### Expected Rates

| Configuration | Repos/Hour | High-Value/Hour |
|---------------|------------|-----------------|
| Single token, no cache | 5,000 | 400 (8%) |
| Single token, 50% cache | 10,000 | 800 (8%) |
| Single token, 80% cache | 25,000 | 2,000 (8%) |
| 10 tokens, 80% cache | 150,000 | 15,000 (10%) |

### Accuracy Evolution

| Discoveries | Accuracy | Explanation |
|-------------|----------|-------------|
| 0-50 (initial) | 60-70% | Baseline from training set |
| 50-200 | 70-75% | Pattern learning begins |
| 200-500 | 75-80% | Patterns solidify |
| 500+ | 80-85% | Mature model |

### Resource Usage

| Resource | Browser | Node.js | CLI (Rust) |
|----------|---------|---------|------------|
| WASM Size | 500KB | 500KB | N/A |
| RAM | 100MB | 200MB | 150MB |
| CPU | 10% | 15% | 8% |
| Storage | 50MB (IndexedDB) | Unlimited (SQLite) | Unlimited |

---

## API Reference (JavaScript)

### Initialize Engine

```javascript
import init, { DiscoveryEngine } from './pkg/gitbank_wasm.js';

await init();

const engine = new DiscoveryEngine(
    'ghp_YOUR_GITHUB_TOKEN',
    'http://localhost:8765' // AgentDB URL
);
```

### Start Discovery

```javascript
const results = await engine.discover(
    ['eosphoros-ai/DB-GPT', 'FunnyWolf/Viper'], // Seeds
    10000, // Max repos
    (progress) => {
        console.log(`Discovered: ${progress.total_discovered}`);
        console.log(`High-value: ${progress.high_value_count}`);
        console.log(`Queue: ${progress.queue_size}`);
    }
);

console.log(`Total: ${results.length} repos`);
```

### Control Discovery

```javascript
// Pause
await engine.pause();

// Resume
await engine.resume();

// Stop
await engine.stop();
```

### Get Statistics

```javascript
const stats = await engine.get_stats();

console.log(stats);
// {
//   total_discovered: 1523,
//   high_value_count: 127,
//   queue_size: 543,
//   api_calls: 1234,
//   cache_hit_rate: 0.67,
//   repos_per_hour: 8432
// }
```

### Export Data

```javascript
// JSON
const json = await engine.export_json();
console.log(json);

// CSV (if implemented)
const csv = await engine.export_csv();
console.log(csv);
```

---

## CLI Commands

### Discover

```bash
gitbank-discovery discover \
  --seeds "eosphoros-ai/DB-GPT,FunnyWolf/Viper" \
  --token $GITHUB_TOKEN \
  --agentdb http://localhost:8765 \
  --max-repos 10000 \
  --output discoveries.json
```

### Resume

```bash
gitbank-discovery resume \
  --checkpoint discoveries.checkpoint.json \
  --output discoveries.json
```

### Export

```bash
gitbank-discovery export \
  --input discoveries.json \
  --format csv \
  --output discoveries.csv
```

### Stats

```bash
gitbank-discovery stats \
  --input discoveries.json
```

---

## Troubleshooting

### Issue: Rate limit exceeded

**Symptom:** Error 403, "API rate limit exceeded"

**Solution:**
1. Wait for rate limit reset (check `x-ratelimit-reset` header)
2. Use multiple tokens (rotation)
3. Increase cache hit rate

### Issue: AgentDB connection failed

**Symptom:** Connection refused, timeout

**Solution:**
1. Start AgentDB: `npx agentdb serve --port 8765`
2. Check firewall
3. Verify URL is correct

### Issue: WASM module too large

**Symptom:** Slow loading, memory errors

**Solution:**
1. Optimize with `wasm-opt -Oz`
2. Strip debug symbols
3. Enable compression (gzip)

### Issue: Discovery not finding high-value repos

**Symptom:** Most repos scored <6.0

**Solution:**
1. Train AgentDB on more opportunities
2. Adjust scoring thresholds
3. Use better seed repos

### Issue: Browser extension crashes

**Symptom:** Extension stops responding

**Solution:**
1. Check memory usage (< 500MB)
2. Reduce max repos or queue size
3. Enable checkpointing (auto-recovery)

---

## Development Workflow

### 1. Setup

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install wasm-pack
curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh

# Install Node.js
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
```

### 2. Build WASM

```bash
cd gitbank-wasm
wasm-pack build --target web --release
```

### 3. Test

```bash
# Unit tests
cargo test

# Integration tests
cargo test --test '*'

# WASM tests
wasm-pack test --headless --firefox
```

### 4. Optimize

```bash
# Optimize WASM
wasm-opt -Oz -o pkg/gitbank_wasm_bg_opt.wasm pkg/gitbank_wasm_bg.wasm

# Check size
ls -lh pkg/
```

### 5. Deploy

```bash
# Browser extension
cd chrome-extension
npm install
npm run build
# Load unpacked in chrome://extensions

# CLI
cd cli
npm install
npm link
gitbank-discovery --version
```

---

## Useful Commands

```bash
# Check GitHub rate limit
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/rate_limit

# Start AgentDB
npx agentdb serve --port 8765

# Train AgentDB
python3 train_agentdb.py

# Build WASM
wasm-pack build --target web --release

# Run CLI
gitbank-discovery discover --seeds "owner/repo"

# Profile WASM
chrome://inspect → Performance → Record

# View logs
chrome://inspect → Console
```

---

## Resources

- **Documentation:** `/media/terry/data/projects/projects/getidea-git-bank/WASM_INFINITE_DISCOVERY_ARCHITECTURE.md`
- **Checklist:** `/media/terry/data/projects/projects/getidea-git-bank/WASM_IMPLEMENTATION_CHECKLIST.md`
- **Training Guide:** `/media/terry/data/projects/projects/getidea-git-bank/AGENTDB_TRAINING_GUIDE.md`
- **GitHub API:** https://docs.github.com/en/rest
- **WASM Guide:** https://rustwasm.github.io/docs/book/
- **wasm-bindgen:** https://rustwasm.github.io/wasm-bindgen/

---

## Quick Decision Tree

**Should I explore this branch?**

```
Is score >= 6.0?
  ├─► Yes: Explore (add children to queue)
  └─► No: Prune (stop recursion)

Is score >= 8.0?
  ├─► Yes: Store as opportunity + train AgentDB
  └─► No: Continue

Is pre_score >= 5.0?
  ├─► Yes: Add to queue
  └─► No: Skip (don't call AgentDB)

Is depth > MAX_DEPTH?
  ├─► Yes: Prune (too deep)
  └─► No: Continue

Is rate_limit < 100?
  ├─► Yes: Wait or rotate token
  └─► No: Continue
```

---

**Document Status:** Complete ✓
**Last Updated:** 2025-10-24
**Version:** 1.0
