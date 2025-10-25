#!/usr/bin/env python3
"""
♾️ Continuous Hidden Gem Discovery System

Runs 24/7 discovering hidden gems and feeding them to the AI.
Never stops. Self-improving. Always learning.

Features:
- Continuous GitHub scanning
- Rate limit management (5000 req/hour with token)
- Real-time database updates
- Pattern learning from discoveries
- Auto-generates ideas from patterns
- Streams to WASM dashboard
"""

import json
import time
import os
import signal
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import deque
import sqlite3

from hidden_gem_discovery import HiddenGemDiscovery, HiddenGemScorer
from ai_idea_generator import PatternLearner, IdeaGenerator

class ContinuousDiscoveryEngine:
    """Runs continuous discovery with rate limiting and learning"""

    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.discovery = HiddenGemDiscovery(self.github_token)

        # State
        self.running = True
        self.total_scanned = 0
        self.gems_found = 0
        self.session_start = datetime.now()

        # Rate limiting (5000 req/hour with token, 60 without)
        self.max_requests_per_hour = 5000 if self.github_token else 60
        self.request_history = deque(maxlen=self.max_requests_per_hour)

        # Database for persistence
        self.db_path = "continuous_discovery.db"
        self.init_database()

        # Pattern learning
        self.learner = PatternLearner()
        self.learned_gems = []

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def init_database(self):
        """Initialize SQLite database for persistent storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovered_gems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                owner TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                stars INTEGER,
                forks INTEGER,
                category TEXT,
                hidden_gem_score REAL,
                agentdb_multiplier REAL,
                base_value TEXT,
                value_with_agentdb TEXT,
                discovered_at TEXT,
                data JSON
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                agentdb_multiplier REAL,
                novelty_score REAL,
                generated_at TEXT,
                data JSON
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_multiplier
            ON discovered_gems(agentdb_multiplier DESC)
        """)

        conn.commit()
        conn.close()

        print(f"✅ Database initialized: {self.db_path}")

    def check_rate_limit(self) -> bool:
        """Check if we can make another request"""
        now = datetime.now()

        # Remove requests older than 1 hour
        while self.request_history and (now - self.request_history[0]) > timedelta(hours=1):
            self.request_history.popleft()

        # Check if under limit
        return len(self.request_history) < self.max_requests_per_hour

    def wait_for_rate_limit(self):
        """Wait if rate limit reached"""
        if not self.check_rate_limit():
            oldest_request = self.request_history[0]
            wait_until = oldest_request + timedelta(hours=1)
            wait_seconds = (wait_until - datetime.now()).total_seconds()

            if wait_seconds > 0:
                print(f"⏸️  Rate limit reached. Waiting {int(wait_seconds)}s (~{int(wait_seconds/60)} minutes)...")
                print(f"   💡 TIP: Add GITHUB_TOKEN for 5000 req/hour limit!")

                # Sleep in chunks and show progress
                for i in range(int(wait_seconds)):
                    if i % 60 == 0:  # Every minute
                        remaining = int(wait_seconds - i)
                        print(f"   ⏳ {remaining}s remaining ({remaining//60}min {remaining%60}s)...", flush=True)
                    time.sleep(1)
                    if not self.running:
                        break

    def record_request(self):
        """Record API request for rate limiting"""
        self.request_history.append(datetime.now())

    def store_gem(self, gem: Dict[str, Any]):
        """Store discovered gem in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO discovered_gems
                (name, owner, url, stars, forks, category, hidden_gem_score,
                 agentdb_multiplier, base_value, value_with_agentdb,
                 discovered_at, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                gem['name'],
                gem['owner'],
                gem['url'],
                gem['stars'],
                gem['forks'],
                gem['category'],
                gem['hidden_gem_score'],
                gem['agentdb_multiplier'],
                gem['base_value'],
                gem['value_with_agentdb'],
                datetime.now().isoformat(),
                json.dumps(gem)
            ))

            conn.commit()
            self.gems_found += 1

        except Exception as e:
            print(f"⚠️  Error storing gem: {e}")
        finally:
            conn.close()

    def get_recent_gems(self, limit: int = 100) -> List[Dict]:
        """Get recently discovered gems"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT data FROM discovered_gems
            ORDER BY discovered_at DESC
            LIMIT ?
        """, (limit,))

        gems = [json.loads(row[0]) for row in cursor.fetchall()]

        conn.close()
        return gems

    def generate_ideas_from_patterns(self):
        """Generate new ideas based on discovered patterns"""
        if len(self.learned_gems) < 10:
            return  # Need enough data

        print(f"\n🤖 Generating ideas from {len(self.learned_gems)} learned gems...")

        # Learn patterns
        self.learner.learn_from_gems(self.learned_gems)

        # Generate ideas
        generator = IdeaGenerator(self.learner.patterns)
        ideas = generator.generate_ideas(count=20)

        # Store top 10 ideas
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for idea in ideas[:10]:
            try:
                cursor.execute("""
                    INSERT INTO generated_ideas
                    (name, category, agentdb_multiplier, novelty_score, generated_at, data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    idea['name'],
                    idea['category'],
                    idea['agentdb_multiplier'],
                    idea['novelty_score'],
                    datetime.now().isoformat(),
                    json.dumps(idea)
                ))
            except:
                pass  # Duplicate

        conn.commit()
        conn.close()

        print(f"✅ Generated and stored {len(ideas[:10])} ideas")

    def print_stats(self):
        """Print current statistics"""
        runtime = datetime.now() - self.session_start
        hours = runtime.total_seconds() / 3600
        rate = self.total_scanned / hours if hours > 0 else 0

        print(f"\n{'='*70}")
        print(f"📊 CONTINUOUS DISCOVERY STATS")
        print(f"{'='*70}")
        print(f"⏱️  Runtime: {int(hours)}h {int((runtime.total_seconds() % 3600) / 60)}m")
        print(f"🔍 Total Scanned: {self.total_scanned:,}")
        print(f"💎 Gems Found: {self.gems_found}")
        print(f"⚡ Scan Rate: {rate:.1f} repos/hour")
        print(f"📊 Rate Limit: {len(self.request_history)}/{self.max_requests_per_hour}")
        print(f"{'='*70}\n")

    def run_discovery_cycle(self):
        """Run one discovery cycle"""

        # UPDATED: AgentDB-focused queries - Find repos with SPEED/LATENCY problems!
        # AgentDB is 10-50x FASTER (2-3ms vs 50-100ms) - find repos that need this!
        all_queries = [
            # TIER 1: Performance Pain Points (AgentDB solves these!)
            ('slow vector search', 100),
            ('high latency embeddings', 100),
            ('vector database performance', 100),
            ('optimize vector search', 100),
            ('vector search slow', 100),
            ('embedding latency', 100),

            # TIER 2: AI Agent Memory Problems
            ('AI agent memory', 100),
            ('chatbot forgets context', 100),
            ('chatbot memory', 100),
            ('persistent agent memory', 100),
            ('AI memory retrieval', 100),
            ('agent context retention', 100),

            # TIER 3: Real-Time RAG Issues
            ('real-time RAG', 100),
            ('RAG performance', 100),
            ('RAG latency', 100),
            ('fast RAG', 100),
            ('semantic search speed', 100),
            ('document retrieval slow', 100),

            # TIER 4: Alternative Implementations (repos we can upgrade)
            ('pinecone alternative', 100),
            ('weaviate performance', 100),
            ('qdrant slow', 100),
            ('chromadb performance', 100),
            ('redis vector', 100),
            ('sqlite embeddings', 100),

            # TIER 5: Specific Use Cases
            ('code assistant memory', 100),
            ('customer support chatbot', 100),
            ('conversational AI memory', 100),
            ('recommendation engine speed', 100),

            # TIER 6: Original high-value patterns (keep best ones)
            ('realtime collaborative', 100),
            ('chat memory', 100),
            ('collaborative editor', 100),
            ('websocket realtime', 100),
        ]

        # Rotate through different queries each cycle to find new repos
        import random
        queries = random.sample(all_queries, min(8, len(all_queries)))  # Increased to 8

        # Add language diversity to find different repos
        # Prioritize Python/TypeScript/JavaScript (most AI projects)
        languages = ['python', 'typescript', 'javascript', 'python', 'typescript', '']
        lang_suffix = random.choice(languages)
        if lang_suffix:
            queries = [(f"{q} language:{lang_suffix}", s) for q, s in queries]

        cycle_gems = []

        for query, max_stars in queries:
            if not self.running:
                break

            print(f"🔍 Searching: {query} (stars < {max_stars})")

            # Wait for rate limit
            self.wait_for_rate_limit()

            # Search with pagination to get different results each time
            # Use modulo of cycle count to rotate through pages
            import math
            page = (self.total_scanned // 1000) % 10  # Rotate through 10 pages

            repos = self.discovery._search_repos(
                f"{query} stars:<{max_stars}",
                max_results=30,
                page=page + 1  # Pages start at 1
            )
            self.record_request()
            self.total_scanned += len(repos)

            if page > 0:
                print(f"   📄 Page {page + 1} (exploring deeper results)")

            # Score each repo
            for repo in repos:
                if not self.running:
                    break

                repo_data = {
                    'name': repo.get('name'),
                    'owner': repo.get('owner', {}).get('login'),
                    'url': repo.get('html_url'),
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'description': repo.get('description'),
                    'language': repo.get('language'),
                    'topics': repo.get('topics', []),
                    'created_at': repo.get('created_at'),
                    'category': self.discovery._categorize(repo),
                }

                score_data = HiddenGemScorer.score_hidden_gem(repo_data)

                # UPDATED: More selective - focus on quality over quantity
                # Star filter: 5-100 stars = real projects, not abandoned
                # Multiplier: >= 15 for higher quality gems
                stars = repo_data.get('stars', 0)
                forks = repo_data.get('forks', 0)
                has_real_traction = stars >= 5 and stars <= 100
                has_forks = forks > 0  # Someone is using it
                high_multiplier = score_data['agentdb_multiplier'] >= 15

                if score_data['is_hidden_gem'] and high_multiplier and (has_real_traction or has_forks):
                    gem = {**repo_data, **score_data}
                    self.store_gem(gem)
                    cycle_gems.append(gem)

                    print(f"  💎 FOUND: {gem['name']} ({gem['stars']}⭐) - {gem['agentdb_multiplier']}x multiplier")

            # Small delay between queries
            time.sleep(2)

        return cycle_gems

    def run(self):
        """Main continuous loop"""

        print("=" * 70)
        print("♾️  CONTINUOUS HIDDEN GEM DISCOVERY")
        print("=" * 70)
        print(f"GitHub Token: {'✅ Authenticated (5000 req/h)' if self.github_token else '⚠️  No token (60 req/h)'}")
        print(f"Database: {self.db_path}")
        print(f"Press Ctrl+C to stop gracefully")
        print("=" * 70)
        print()

        cycle_count = 0

        try:
            while self.running:
                cycle_count += 1
                print(f"\n{'='*70}")
                print(f"🔄 DISCOVERY CYCLE #{cycle_count}")
                print(f"{'='*70}")

                # Run discovery
                cycle_gems = self.run_discovery_cycle()

                # Add to learned patterns
                self.learned_gems.extend(cycle_gems)

                # Generate ideas every 5 cycles
                if cycle_count % 5 == 0 and self.learned_gems:
                    self.generate_ideas_from_patterns()

                # Print stats every cycle
                self.print_stats()

                # Export results every 10 cycles
                if cycle_count % 10 == 0:
                    self.export_results()

                print(f"⏳ Cycle complete. Starting next cycle...")
                time.sleep(5)

        except KeyboardInterrupt:
            self.handle_shutdown()

    def export_results(self):
        """Export current results to JSON"""
        output_file = f"continuous_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        gems = self.get_recent_gems(limit=1000)

        with open(output_file, 'w') as f:
            json.dump({
                'exported_at': datetime.now().isoformat(),
                'session_start': self.session_start.isoformat(),
                'total_scanned': self.total_scanned,
                'gems_found': self.gems_found,
                'gems': gems[:100],  # Top 100
            }, f, indent=2)

        print(f"💾 Exported to: {output_file}")

    def handle_shutdown(self, signum=None, frame=None):
        """Handle graceful shutdown"""
        print("\n\n⏸️  Shutting down gracefully...")
        self.running = False
        self.export_results()
        self.print_stats()

        # Final summary
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM discovered_gems")
        total_gems = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM generated_ideas")
        total_ideas = cursor.fetchone()[0]

        conn.close()

        print(f"\n{'='*70}")
        print(f"📊 FINAL STATISTICS")
        print(f"{'='*70}")
        print(f"Total Gems Discovered: {total_gems}")
        print(f"Total Ideas Generated: {total_ideas}")
        print(f"Database: {self.db_path}")
        print(f"{'='*70}\n")

        sys.exit(0)


def main():
    """Start continuous discovery"""

    # Get GitHub token
    github_token = os.getenv('GITHUB_TOKEN')

    if not github_token:
        print("⚠️  WARNING: No GITHUB_TOKEN found")
        print("   Set with: export GITHUB_TOKEN=your_token_here")
        print("   Rate limit: 60 requests/hour without token")
        print("   Rate limit: 5000 requests/hour with token")
        print("   Continuing anyway...")
        print()

    # Start engine
    engine = ContinuousDiscoveryEngine(github_token)
    engine.run()


if __name__ == '__main__':
    main()
