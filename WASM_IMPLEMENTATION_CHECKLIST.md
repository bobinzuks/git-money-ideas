# WASM Infinite Discovery - Implementation Checklist

**Project:** GitBank WASM Discovery Engine
**Timeline:** 10 weeks
**Status:** Ready to Start

---

## Quick Reference

### System Overview
```
User stars Repo A → Find stargazers → Get their repos → Score with AgentDB
    → If score >= 8.0: Store as opportunity
    → If score >= 6.0: Explore children (follow success path)
    → If score < 6.0: Prune branch (dead end)
```

### Expected Performance
- **Discovery Rate:** 5K-50K repos/hour (depending on instances)
- **Accuracy:** 70% initially → 85% after 500 discoveries
- **Resource Usage:** 500KB WASM, 100MB RAM, 10% CPU

---

## Phase 1: Core WASM Module (Weeks 1-2)

### 1.1 Project Setup
- [ ] Create `gitbank-wasm/` directory
- [ ] Initialize Cargo project: `cargo init --lib`
- [ ] Configure `Cargo.toml` with WASM dependencies
  - [ ] wasm-bindgen
  - [ ] wasm-bindgen-futures
  - [ ] js-sys, web-sys
  - [ ] serde, serde_json
  - [ ] reqwest (WASM-compatible)
- [ ] Setup webpack for JavaScript bindings
- [ ] Create npm package structure

### 1.2 Graph Traversal Core
- [ ] Implement priority queue (BinaryHeap)
  - [ ] Max-heap for best-first search
  - [ ] Custom comparator for (priority, repo_id)
- [ ] Implement visited set (HashSet)
  - [ ] Store repo IDs
  - [ ] O(1) membership testing
- [ ] Implement Bloom filter
  - [ ] 1M capacity, 1% false positive
  - [ ] Space-efficient deduplication
- [ ] Cycle detection logic
  - [ ] Check both visited set and Bloom filter
  - [ ] Early exit for already-visited nodes

### 1.3 GitHub API Client
- [ ] Create `GitHubClient` struct
  - [ ] reqwest::Client initialization
  - [ ] Authentication header injection
- [ ] Implement endpoints:
  - [ ] `get_repo(owner, name)` → Repository
  - [ ] `get_stargazers(owner, name, per_page)` → Vec<User>
  - [ ] `get_user_repos(username)` → Vec<Repository>
- [ ] Error handling
  - [ ] 404: Repository not found
  - [ ] 403: Rate limit exceeded
  - [ ] 401: Invalid token
- [ ] Response parsing
  - [ ] Deserialize JSON to Rust structs
  - [ ] Extract rate limit headers

### 1.4 Rate Limiter
- [ ] Create `RateLimiter` struct
  - [ ] Track remaining requests
  - [ ] Track reset timestamp
- [ ] Implement `wait_if_needed()`
  - [ ] Check remaining < 100
  - [ ] Sleep until reset if exhausted
- [ ] Token rotation
  - [ ] Support multiple tokens
  - [ ] Rotate when rate limit hit
  - [ ] Track which token is active
- [ ] Rate limit header parsing
  - [ ] `x-ratelimit-remaining`
  - [ ] `x-ratelimit-reset`

### 1.5 WASM Bindings
- [ ] Create `DiscoveryEngine` struct with `#[wasm_bindgen]`
- [ ] Implement JavaScript API:
  - [ ] `new(github_token, agentdb_url)` → DiscoveryEngine
  - [ ] `discover(seeds, max_repos, on_progress)` → Results
  - [ ] `pause()` → void
  - [ ] `resume()` → void
  - [ ] `stop()` → void
  - [ ] `get_stats()` → Statistics
  - [ ] `export_json()` → String
- [ ] Progress callback
  - [ ] Convert Rust progress to JavaScript object
  - [ ] Call JavaScript function from Rust

### 1.6 Testing
- [ ] Unit tests:
  - [ ] Priority queue ordering
  - [ ] Visited set deduplication
  - [ ] Bloom filter false positive rate
  - [ ] Rate limiter timing
- [ ] Integration tests:
  - [ ] Mock GitHub API responses
  - [ ] Test full traversal on small graph
  - [ ] Test rate limit handling
- [ ] Performance benchmarks:
  - [ ] Measure traversal speed (repos/sec)
  - [ ] Measure memory usage
  - [ ] Measure WASM module size

**Milestone:** WASM module compiles, basic traversal works, <1MB size

---

## Phase 2: AgentDB Integration (Weeks 3-4)

### 2.1 AgentDB Client (WASM)
- [ ] Create `AgentDBClient` struct
  - [ ] HTTP client (reqwest)
  - [ ] Base URL configuration
- [ ] Implement methods:
  - [ ] `store_vector(id, embedding, metadata)` → Result
  - [ ] `search_similar(embedding, top_k)` → Vec<SearchResult>
  - [ ] `batch_search(embeddings)` → Vec<Vec<SearchResult>>
- [ ] Health check
  - [ ] Ping AgentDB on initialization
  - [ ] Retry with exponential backoff
- [ ] Error handling
  - [ ] Connection refused
  - [ ] Timeout
  - [ ] Invalid response

### 2.2 Embedding Generation
- [ ] Implement `generate_simple_embedding(text)` → Vec<f32>
  - [ ] 128-dimensional vector
  - [ ] Feature extraction:
    - [ ] Text length normalization
    - [ ] Keyword detection (AI, security, API, etc.)
    - [ ] Language indicators
    - [ ] Commercial keywords
  - [ ] Normalization (unit vector)
- [ ] Implement `generate_opportunity_embedding(repo)` → Vec<f32>
  - [ ] Combine: name, description, language, topics
  - [ ] Call `generate_simple_embedding()`
- [ ] Caching
  - [ ] LRU cache (1000 embeddings)
  - [ ] Cache key: repo ID
  - [ ] Invalidation: never (embeddings are stable)

### 2.3 Scoring Algorithm
- [ ] Implement `score_repository(repo)` → f32
  - [ ] Generate embedding for repo
  - [ ] Search AgentDB for similar repos (top_k=10)
  - [ ] Weighted score calculation:
    - [ ] score = Σ(similarity × known_revenue_score) / Σ(similarity)
  - [ ] Apply quality multiplier:
    - [ ] Active maintenance: 1.2x
    - [ ] High stars (>1000): 1.1x
    - [ ] High stars (>5000): 1.2x
    - [ ] High fork ratio (>0.5): 0.8x
    - [ ] Has documentation: 1.1x
    - [ ] Commercial keywords: 1.3x
  - [ ] Normalize to 0-10 scale
- [ ] Implement `quick_score(repo_metadata)` → f32
  - [ ] Fast pre-filter (no AgentDB call)
  - [ ] Based on: stars, language, keywords, recency
  - [ ] Purpose: Reduce expensive AgentDB calls

### 2.4 Continuous Learning
- [ ] Implement `train_incremental(repo, score)` → Result
  - [ ] Generate embedding
  - [ ] Prepare metadata (stars, language, category, score)
  - [ ] Store in AgentDB
- [ ] Trigger training:
  - [ ] After every high-value discovery (score >= 8.0)
  - [ ] Async (don't block discovery)
- [ ] Pattern extraction (background task):
  - [ ] Every 100 discoveries
  - [ ] Analyze language distribution
  - [ ] Analyze category distribution
  - [ ] Analyze keyword frequency
  - [ ] Update scoring weights

### 2.5 Initial Training
- [ ] Load existing opportunities:
  - [ ] Read `detailed_opportunities.json`
  - [ ] Read `strategic_monetization_report.json`
- [ ] Train on 50+ opportunities:
  - [ ] Generate embeddings
  - [ ] Store in AgentDB with metadata
  - [ ] Validate training (similarity search)
- [ ] Measure accuracy:
  - [ ] Test set: 10 opportunities (held out)
  - [ ] Check if similar repos found
  - [ ] Target: >70% accuracy

### 2.6 Testing
- [ ] Unit tests:
  - [ ] Embedding generation (dimension, normalization)
  - [ ] Scoring algorithm (weighted average)
  - [ ] Quality multiplier (edge cases)
- [ ] Integration tests:
  - [ ] Train on sample opportunities
  - [ ] Test similarity search
  - [ ] Measure accuracy
- [ ] Performance benchmarks:
  - [ ] Embedding generation time (<10ms)
  - [ ] AgentDB search time (<100ms)
  - [ ] Scoring time (<100ms)

**Milestone:** AgentDB integration complete, scoring accuracy >70%, <100ms per score

---

## Phase 3: Storage & Checkpoints (Week 5)

### 3.1 IndexedDB Backend (Browser)
- [ ] Create `IndexedDBStorage` struct
- [ ] Initialize database:
  - [ ] Database name: "gitbank-discovery"
  - [ ] Object stores: repos, edges, visited, checkpoints
  - [ ] Indexes: score, stars, language, discovered_at
- [ ] Implement methods:
  - [ ] `store_repo(repo, score)` → Result
  - [ ] `get_repo(id)` → Option<Repository>
  - [ ] `get_high_value_repos(min_score, limit)` → Vec<Repository>
  - [ ] `mark_visited(repo_id)` → Result
  - [ ] `is_visited(repo_id)` → bool
- [ ] Error handling:
  - [ ] Quota exceeded
  - [ ] Transaction failed

### 3.2 SQLite WASM Backend (Node.js)
- [ ] Create `SQLiteStorage` struct
- [ ] Initialize database:
  - [ ] Create tables: repos, edges, visited, checkpoints
  - [ ] Create indexes: score, stars, language
- [ ] Implement methods (same as IndexedDB):
  - [ ] `store_repo(repo, score)` → Result
  - [ ] `get_repo(id)` → Option<Repository>
  - [ ] `get_high_value_repos(min_score, limit)` → Vec<Repository>
  - [ ] `mark_visited(repo_id)` → Result
  - [ ] `is_visited(repo_id)` → bool
- [ ] Connection pooling
- [ ] Transaction management

### 3.3 Checkpoint System
- [ ] Create `Checkpoint` struct:
  - [ ] timestamp: String
  - [ ] queue: Vec<(f32, String)>
  - [ ] visited: HashSet<String>
  - [ ] stats: Statistics
- [ ] Implement `save_checkpoint()` → Result
  - [ ] Serialize state to JSON
  - [ ] Store in storage backend
- [ ] Implement `load_checkpoint(data)` → Result<DiscoveryEngine>
  - [ ] Deserialize JSON
  - [ ] Restore queue, visited set, stats
- [ ] Auto-save:
  - [ ] Every 5 minutes
  - [ ] On pause/stop
  - [ ] On error/crash

### 3.4 Export Functionality
- [ ] Implement `export_json()` → String
  - [ ] Serialize all discovered repos
  - [ ] Include metadata, scores, edges
- [ ] Implement `export_csv()` → String
  - [ ] Headers: id, name, owner, stars, score, category, url
  - [ ] One repo per row
- [ ] Implement `export_graph()` → String
  - [ ] GraphML or DOT format
  - [ ] Nodes: repos
  - [ ] Edges: user connections

### 3.5 Testing
- [ ] Unit tests:
  - [ ] Store/retrieve repos
  - [ ] Checkpoint serialization/deserialization
  - [ ] Export formats (valid JSON/CSV)
- [ ] Integration tests:
  - [ ] Store 10K repos
  - [ ] Query by score
  - [ ] Checkpoint recovery
- [ ] Performance benchmarks:
  - [ ] Store rate (repos/sec)
  - [ ] Query time (<100ms)
  - [ ] Checkpoint size

**Milestone:** Can store 100K+ repos, checkpoint/resume works, export formats valid

---

## Phase 4: Browser Extension (Week 6)

### 4.1 Extension Structure
- [ ] Create directory: `chrome-extension/`
- [ ] Create `manifest.json` (Manifest V3):
  - [ ] Permissions: storage, unlimitedStorage, alarms
  - [ ] Host permissions: api.github.com, localhost:8765
  - [ ] Background service worker
  - [ ] Action (popup)
  - [ ] Content scripts
- [ ] Create icon set (16x16, 48x48, 128x128)

### 4.2 Background Service Worker
- [ ] Create `background.js`:
  - [ ] Import WASM module
  - [ ] Initialize DiscoveryEngine
  - [ ] Listen for messages from popup
- [ ] Implement message handlers:
  - [ ] `start_discovery` → Start engine
  - [ ] `stop_discovery` → Stop engine
  - [ ] `pause_discovery` → Pause engine
  - [ ] `resume_discovery` → Resume engine
  - [ ] `get_stats` → Return statistics
  - [ ] `export_data` → Return JSON/CSV
- [ ] Progress updates:
  - [ ] Send messages to popup
  - [ ] Update badge with count
- [ ] Persistence:
  - [ ] Save state to chrome.storage
  - [ ] Restore on browser restart

### 4.3 Popup UI
- [ ] Create `popup/index.html`:
  - [ ] Input: seed repos (textarea)
  - [ ] Input: max repos (number)
  - [ ] Buttons: Start, Stop, Pause, Resume
  - [ ] Stats display: discovered, high-value, queue size
  - [ ] Progress bar
  - [ ] Export buttons: JSON, CSV
- [ ] Create `popup/popup.js`:
  - [ ] Load saved seeds from storage
  - [ ] Send messages to background worker
  - [ ] Update UI on progress
  - [ ] Handle errors
- [ ] Create `popup/styles.css`:
  - [ ] Modern, clean design
  - [ ] Responsive layout
  - [ ] Dark mode support

### 4.4 Content Script (GitHub Injection)
- [ ] Create `content/github_inject.js`:
  - [ ] Detect GitHub repo pages
  - [ ] Inject "Discover Similar" button
  - [ ] On click: Send repo to background worker as seed
- [ ] CSS injection:
  - [ ] Style injected button to match GitHub UI

### 4.5 Options Page
- [ ] Create `options/options.html`:
  - [ ] Input: GitHub token (password)
  - [ ] Input: AgentDB URL
  - [ ] Input: Discovery settings (thresholds, limits)
  - [ ] Save button
- [ ] Create `options/options.js`:
  - [ ] Load settings from chrome.storage.sync
  - [ ] Save settings on submit
  - [ ] Validate inputs

### 4.6 Testing
- [ ] Manual testing in Chrome
- [ ] Test all features:
  - [ ] Start/stop/pause/resume
  - [ ] Progress updates
  - [ ] Export functionality
  - [ ] Content script injection
  - [ ] Settings persistence
- [ ] Test edge cases:
  - [ ] Browser restart during discovery
  - [ ] Invalid GitHub token
  - [ ] AgentDB offline
  - [ ] Network errors

**Milestone:** Extension installs, discovery runs, UI updates in real-time

---

## Phase 5: Node.js CLI (Week 7)

### 5.1 CLI Structure
- [ ] Create npm package: `gitbank-discovery`
- [ ] Create `package.json`:
  - [ ] Dependencies: commander, chalk, ora, cli-progress
  - [ ] Binary: gitbank-discovery
- [ ] Create `src/cli.js`:
  - [ ] Import WASM module
  - [ ] Parse command-line arguments

### 5.2 Commands
- [ ] Implement `discover` command:
  - [ ] Arguments: --seeds, --token, --agentdb, --max-repos, --output
  - [ ] Start discovery
  - [ ] Show progress bar (cli-progress)
  - [ ] Save results to file
- [ ] Implement `resume` command:
  - [ ] Arguments: --checkpoint
  - [ ] Load checkpoint
  - [ ] Resume discovery
- [ ] Implement `export` command:
  - [ ] Arguments: --input, --format (json/csv), --output
  - [ ] Read discovered repos
  - [ ] Export to format
- [ ] Implement `stats` command:
  - [ ] Arguments: --input
  - [ ] Show statistics:
    - [ ] Total discovered
    - [ ] High-value count
    - [ ] Category breakdown
    - [ ] Language breakdown

### 5.3 Progress Reporting
- [ ] Real-time progress bar (ora)
- [ ] Stats display:
  - [ ] Discovered: X
  - [ ] High-value: Y
  - [ ] Queue size: Z
  - [ ] API calls: A
  - [ ] Rate limit: B remaining
- [ ] Colored output (chalk):
  - [ ] Green: success
  - [ ] Yellow: warning
  - [ ] Red: error
  - [ ] Blue: info

### 5.4 Error Handling
- [ ] Invalid token
- [ ] AgentDB offline
- [ ] File I/O errors
- [ ] Network errors
- [ ] Graceful shutdown (Ctrl+C)

### 5.5 Testing
- [ ] Test all commands
- [ ] Test error handling
- [ ] Test checkpoint recovery
- [ ] Test export formats
- [ ] Test on Linux/Mac/Windows

**Milestone:** CLI works on all platforms, can run for hours, clear progress reporting

---

## Phase 6: Optimization & Scaling (Week 8)

### 6.1 Multi-Token Rotation
- [ ] Support multiple GitHub tokens:
  - [ ] Load from environment: GITHUB_TOKEN_1, GITHUB_TOKEN_2, ...
  - [ ] Load from config file: tokens.json
- [ ] Automatic rotation:
  - [ ] When rate limit hit
  - [ ] Round-robin
- [ ] Per-token rate limit tracking

### 6.2 Parallel Instances
- [ ] Implement `parallel_discover()`:
  - [ ] Split seeds across N instances
  - [ ] Each instance runs in separate async task
  - [ ] Each uses different token
- [ ] Shared cache:
  - [ ] Use Arc<Mutex<Cache>> for thread-safe sharing
  - [ ] Deduplication across instances
- [ ] Result merging:
  - [ ] Combine results from all instances
  - [ ] Deduplicate

### 6.3 Aggressive Caching
- [ ] Multi-layer cache:
  - [ ] L1: In-memory LRU (10K repos)
  - [ ] L2: IndexedDB/SQLite (100K repos)
  - [ ] L3: AgentDB vector search (semantic)
- [ ] Cache statistics:
  - [ ] Hit rate per layer
  - [ ] Total hits vs misses
- [ ] Cache invalidation:
  - [ ] Time-based (1 hour TTL)
  - [ ] LRU eviction

### 6.4 Smart Pruning
- [ ] Refine pruning heuristics:
  - [ ] Analyze which pruned branches had hidden gems
  - [ ] Adjust thresholds dynamically
- [ ] Implement adaptive thresholds:
  - [ ] Increase threshold if queue too large
  - [ ] Decrease threshold if not finding enough high-value
- [ ] Category-specific pruning:
  - [ ] Different thresholds for security vs education

### 6.5 Batch API Requests
- [ ] Implement GitHub GraphQL API:
  - [ ] Batch multiple repo requests
  - [ ] Batch multiple stargazer requests
- [ ] Batching strategy:
  - [ ] Collect 50 requests
  - [ ] Send as single GraphQL query
  - [ ] Parse batched response

### 6.6 Performance Benchmarks
- [ ] Load testing:
  - [ ] Discover 100K repos
  - [ ] Measure: time, memory, CPU
- [ ] Rate limit testing:
  - [ ] Verify no violations
  - [ ] Measure effective rate (repos/hour)
- [ ] Memory profiling:
  - [ ] Identify leaks
  - [ ] Optimize data structures
- [ ] WASM size optimization:
  - [ ] Use wasm-opt -Oz
  - [ ] Strip debug symbols
  - [ ] Target: <500KB

**Milestone:** 10K+ repos/hour, <500MB memory, no rate limit violations

---

## Phase 7: Production Deployment (Weeks 9-10)

### 7.1 Documentation
- [ ] User guide:
  - [ ] Installation instructions
  - [ ] Getting started tutorial
  - [ ] Configuration guide
  - [ ] Troubleshooting
- [ ] API reference:
  - [ ] JavaScript API (WASM)
  - [ ] CLI commands
  - [ ] Configuration options
- [ ] Developer guide:
  - [ ] Architecture overview
  - [ ] Contributing guide
  - [ ] Build instructions

### 7.2 Video Tutorial
- [ ] Record 10-minute video:
  - [ ] Installation
  - [ ] Browser extension demo
  - [ ] CLI demo
  - [ ] Export and analysis
- [ ] Publish to YouTube
- [ ] Embed in README

### 7.3 Chrome Web Store Submission
- [ ] Prepare assets:
  - [ ] Screenshots (5)
  - [ ] Promotional image (440x280)
  - [ ] Description (short and full)
- [ ] Privacy policy page
- [ ] Submit for review
- [ ] Respond to feedback
- [ ] Publish

### 7.4 npm Package Publication
- [ ] Final testing:
  - [ ] npm install test
  - [ ] All commands work
- [ ] Versioning:
  - [ ] Semantic versioning
  - [ ] Changelog
- [ ] Publish to npm:
  - [ ] npm publish
  - [ ] Add keywords, homepage, repository
- [ ] Create GitHub release:
  - [ ] Tag version
  - [ ] Attach binaries (Linux, Mac, Windows)
  - [ ] Release notes

### 7.5 Beta Testing
- [ ] Recruit 10 beta testers
- [ ] Provide test accounts (GitHub tokens)
- [ ] Collect feedback:
  - [ ] Bugs
  - [ ] Feature requests
  - [ ] UX issues
- [ ] Fix critical bugs
- [ ] Iterate on UX

### 7.6 Launch
- [ ] Announce on:
  - [ ] Twitter/X
  - [ ] Reddit (r/webdev, r/programming)
  - [ ] Hacker News
  - [ ] Product Hunt
- [ ] Blog post:
  - [ ] Technical deep dive
  - [ ] Use cases
  - [ ] Results (repos discovered, opportunities found)
- [ ] Monitor:
  - [ ] Extension installs
  - [ ] npm downloads
  - [ ] GitHub stars
  - [ ] User feedback

**Milestone:** Extension live on Chrome Web Store, npm package published, docs complete

---

## Success Metrics

### Technical Metrics
- [ ] WASM module size: <500KB (compressed)
- [ ] Discovery rate: 5K-50K repos/hour
- [ ] Pattern accuracy: >70% initially, >85% after 500 discoveries
- [ ] Memory usage: <500MB
- [ ] CPU usage: <20% (single core)
- [ ] Rate limit violations: 0

### User Metrics
- [ ] Chrome Web Store installs: 100+ in first month
- [ ] npm downloads: 500+ in first month
- [ ] GitHub stars: 50+ in first month
- [ ] Active users: 20+ weekly

### Business Metrics
- [ ] Repositories discovered: 100K+ in first month
- [ ] High-value opportunities: 10K+ in first month
- [ ] Actionable opportunities: 1K+ in first month
- [ ] Potential deals: 100+ in first month

---

## Risk Mitigation

### Technical Risks
- **WASM compilation issues** → Use proven tools (wasm-pack, wasm-bindgen)
- **GitHub rate limits** → Multi-token rotation, aggressive caching
- **AgentDB offline** → Fallback to simple scoring
- **Browser extension rejected** → Follow Chrome Web Store guidelines strictly
- **Performance issues** → Optimize early, benchmark continuously

### Business Risks
- **Low adoption** → Marketing, tutorials, free tier
- **Competition** → Differentiate with AI-powered scoring
- **GitHub API changes** → Monitor changes, adapt quickly

---

## Next Steps

1. **Review this checklist** with team
2. **Set up development environment** (Rust, Node.js, wasm-pack)
3. **Create project repositories** (gitbank-wasm, chrome-extension)
4. **Begin Phase 1** (Core WASM Module)
5. **Parallel: Train AgentDB** on existing 50+ opportunities

---

## Resources

### Development Tools
- Rust: https://rustup.rs/
- wasm-pack: https://rustwasm.github.io/wasm-pack/
- Node.js: https://nodejs.org/
- Chrome Extension Docs: https://developer.chrome.com/docs/extensions/

### Dependencies
- wasm-bindgen: https://rustwasm.github.io/wasm-bindgen/
- reqwest: https://docs.rs/reqwest/
- serde: https://serde.rs/
- tokio: https://tokio.rs/

### Learning Resources
- WASM by Example: https://wasmbyexample.dev/
- Chrome Extension Tutorial: https://developer.chrome.com/docs/extensions/mv3/getstarted/
- GitHub API: https://docs.github.com/en/rest

---

**Document Status:** Complete ✓
**Ready to Start:** Yes
**Estimated Completion:** 10 weeks
**Next Task:** Phase 1.1 - Project Setup
