#!/usr/bin/env python3
"""
Simple Vector Database Training - Alternative to AgentDB

Since AgentDB doesn't have a clear server mode, this uses a simple
SQLite-based vector database to train on your opportunities.

This provides the same functionality:
1. Stores opportunity embeddings
2. Enables similarity search
3. Pattern recognition
"""

import json
import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pickle

class SimpleVectorDB:
    """Simple vector database using SQLite"""

    def __init__(self, db_path: str = "opportunity_vectors.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """Create database schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id TEXT PRIMARY KEY,
                embedding BLOB NOT NULL,
                metadata TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def store(self, repo_id: str, embedding: List[float], metadata: Dict[str, Any]):
        """Store opportunity with embedding"""
        embedding_blob = pickle.dumps(np.array(embedding, dtype=np.float32))
        metadata_json = json.dumps(metadata)

        self.conn.execute("""
            INSERT OR REPLACE INTO opportunities (id, embedding, metadata)
            VALUES (?, ?, ?)
        """, (repo_id, embedding_blob, metadata_json))
        self.conn.commit()

    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """Find similar opportunities using cosine similarity"""
        query_vec = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)

        if query_norm == 0:
            return []

        query_vec = query_vec / query_norm

        cursor = self.conn.execute("SELECT id, embedding, metadata FROM opportunities")
        results = []

        for row in cursor:
            repo_id, embedding_blob, metadata_json = row
            stored_vec = pickle.loads(embedding_blob)

            # Cosine similarity
            similarity = np.dot(query_vec, stored_vec)

            metadata = json.loads(metadata_json)
            results.append((repo_id, float(similarity), metadata))

        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def get_all(self) -> List[Tuple[str, List[float], Dict]]:
        """Get all stored opportunities"""
        cursor = self.conn.execute("SELECT id, embedding, metadata FROM opportunities")
        results = []

        for row in cursor:
            repo_id, embedding_blob, metadata_json = row
            embedding = pickle.loads(embedding_blob).tolist()
            metadata = json.loads(metadata_json)
            results.append((repo_id, embedding, metadata))

        return results

    def close(self):
        """Close database connection"""
        self.conn.close()


def generate_embedding(text: str, dim: int = 128) -> List[float]:
    """
    Generate a simple but effective embedding based on text features.
    Uses keyword matching and TF-IDF-like weighting.
    """
    embedding = np.zeros(dim, dtype=np.float32)
    text_lower = text.lower()
    words = text_lower.split()

    # Basic statistics (dimensions 0-9)
    embedding[0] = min(len(text) / 1000.0, 1.0)  # Length
    embedding[1] = min(len(words) / 100.0, 1.0)  # Word count

    # Category indicators (dimensions 2-9)
    categories = {
        2: ['ai', 'ml', 'machine learning', 'neural', 'llm', 'gpt'],
        3: ['security', 'cyber', 'authentication', 'encryption', 'vulnerability'],
        4: ['platform', 'service', 'saas', 'cloud', 'infrastructure'],
        5: ['api', 'sdk', 'library', 'framework', 'toolkit'],
        6: ['enterprise', 'business', 'corporate', 'commercial'],
        7: ['developer', 'devops', 'ci/cd', 'deployment', 'automation'],
        8: ['analytics', 'monitoring', 'observability', 'metrics', 'dashboard'],
        9: ['database', 'storage', 'sql', 'nosql', 'data'],
    }

    for dim_idx, keywords in categories.items():
        if any(kw in text_lower for kw in keywords):
            embedding[dim_idx] = 0.8

    # Language features (dimensions 10-19)
    languages = ['python', 'javascript', 'java', 'go', 'rust', 'c++', 'typescript', 'php', 'ruby', 'c#']
    for i, lang in enumerate(languages):
        if i + 10 < dim and lang in text_lower:
            embedding[i + 10] = 0.7

    # Technology keywords (dimensions 20-60)
    tech_keywords = [
        'docker', 'kubernetes', 'aws', 'azure', 'gcp',
        'react', 'vue', 'angular', 'node', 'express',
        'postgres', 'mysql', 'mongodb', 'redis', 'elasticsearch',
        'kafka', 'rabbitmq', 'grpc', 'rest', 'graphql',
        'tensorflow', 'pytorch', 'scikit', 'pandas', 'numpy',
        'microservices', 'serverless', 'lambda', 'container',
        'testing', 'junit', 'pytest', 'selenium', 'cypress',
        'git', 'github', 'gitlab', 'jenkins', 'travis',
    ]

    for i, keyword in enumerate(tech_keywords):
        if i + 20 < dim and keyword in text_lower:
            embedding[i + 20] = 0.5

    # Monetization keywords (dimensions 60-80)
    monetization_keywords = [
        'subscription', 'license', 'freemium', 'pricing',
        'revenue', 'profit', 'business model', 'monetize',
        'enterprise', 'consulting', 'support', 'training',
        'marketplace', 'ecommerce', 'payment', 'billing',
        'customer', 'user', 'client', 'saas',
    ]

    for i, keyword in enumerate(monetization_keywords):
        if i + 60 < dim and keyword in text_lower:
            embedding[i + 60] = 0.6

    # Normalize to unit vector
    magnitude = np.linalg.norm(embedding)
    if magnitude > 0:
        embedding = embedding / magnitude

    return embedding.tolist()


def train_from_opportunities(db: SimpleVectorDB, opportunities: List[Dict[str, Any]]) -> int:
    """Train database from opportunity data"""

    success_count = 0

    for opp in opportunities:
        try:
            # Extract data
            repo_info = opp.get('repository', {})
            mon_info = opp.get('monetization', {})
            owner_info = opp.get('owner', {})
            market_info = opp.get('market_analysis', {})

            # Generate combined text for embedding
            combined_text = f"{repo_info.get('name', '')} {repo_info.get('description', '')} " \
                           f"{repo_info.get('category', '')} {repo_info.get('language', '')} " \
                           f"{mon_info.get('why_fast', '')} {' '.join(mon_info.get('strategies', []))}"

            # Generate embedding
            embedding = generate_embedding(combined_text)

            # Prepare metadata
            metadata = {
                'project': opp.get('project', ''),
                'owner': owner_info.get('username', ''),
                'company': owner_info.get('company'),
                'location': owner_info.get('location'),
                'stars': repo_info.get('stars', 0),
                'language': repo_info.get('language', ''),
                'category': repo_info.get('category', ''),
                'description': repo_info.get('description', ''),
                'revenue_score': mon_info.get('revenue_potential_score', 0),
                'estimated_revenue': mon_info.get('estimated_annual_revenue', ''),
                'time_to_market': mon_info.get('time_to_market', ''),
                'investment_needed': mon_info.get('required_investment', ''),
                'strategies': mon_info.get('strategies', []),
                'why_fast': mon_info.get('why_fast', ''),
                'url': repo_info.get('url', ''),
            }

            # Store in database
            repo_id = f"{owner_info.get('username', 'unknown')}/{repo_info.get('name', 'unknown')}"
            db.store(repo_id, embedding, metadata)

            success_count += 1

            if success_count % 5 == 0:
                print(f"✅ Stored {success_count} opportunities: {repo_id}")

        except Exception as e:
            print(f"❌ Error storing opportunity: {e}")

    return success_count


def validate_training(db: SimpleVectorDB):
    """Test similarity search to validate training"""

    print("\n🧪 Validating training quality...")

    # Test queries
    test_queries = [
        ("security platform for enterprise red team testing", "Security"),
        ("python machine learning framework with high stars", "AI/ML"),
        ("developer productivity tool with automation", "Developer Tools"),
    ]

    for query_text, expected_category in test_queries:
        print(f"\n🔍 Test Query: '{query_text}'")
        print(f"   Expected category: {expected_category}")

        query_embedding = generate_embedding(query_text)
        results = db.search_similar(query_embedding, top_k=5)

        print(f"\n📊 Top 5 Similar Opportunities:")

        for i, (repo_id, score, metadata) in enumerate(results, 1):
            print(f"\n{i}. {metadata.get('project', 'Unknown')} (Score: {score:.3f})")
            print(f"   Repository: {repo_id}")
            print(f"   Category: {metadata.get('category', 'N/A')}")
            print(f"   Revenue Score: {metadata.get('revenue_score', 0)}/10")
            print(f"   Estimated Revenue: {metadata.get('estimated_revenue', 'N/A')}")
            print(f"   Stars: {metadata.get('stars', 0):,}")


def extract_patterns(db: SimpleVectorDB):
    """Analyze stored opportunities to extract patterns"""

    print("\n🔍 Extracting Success Patterns...")

    all_opps = db.get_all()

    # Group by category
    by_category = {}
    by_language = {}
    high_revenue = []

    for repo_id, embedding, metadata in all_opps:
        category = metadata.get('category', 'Unknown')
        language = metadata.get('language', 'Unknown')
        revenue_score = metadata.get('revenue_score', 0)

        by_category.setdefault(category, []).append(metadata)
        by_language.setdefault(language, []).append(metadata)

        if revenue_score >= 8.0:
            high_revenue.append(metadata)

    print(f"\n📊 Dataset Statistics:")
    print(f"   Total Opportunities: {len(all_opps)}")
    print(f"   Unique Categories: {len(by_category)}")
    print(f"   Unique Languages: {len(by_language)}")
    print(f"   High Revenue (≥8.0): {len(high_revenue)}")

    print(f"\n🏆 Top Categories by Count:")
    for cat, opps in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        avg_score = np.mean([o.get('revenue_score', 0) for o in opps])
        print(f"   {cat}: {len(opps)} projects (avg score: {avg_score:.1f})")

    print(f"\n💻 Top Languages:")
    for lang, opps in sorted(by_language.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        avg_stars = np.mean([o.get('stars', 0) for o in opps])
        print(f"   {lang}: {len(opps)} projects (avg stars: {avg_stars:.0f})")

    print(f"\n🎯 High Revenue Patterns (score ≥ 8.0):")
    for opp in high_revenue[:5]:
        print(f"   • {opp['project']}: {opp['category']} ({opp['stars']:,} stars)")
        print(f"     Revenue: {opp['estimated_revenue']}")


def main():
    """Main training pipeline"""

    print("=" * 70)
    print("🎓 SIMPLE VECTOR DATABASE TRAINING")
    print("=" * 70)

    # Initialize database
    db = SimpleVectorDB("opportunity_vectors.db")
    print("✅ Database initialized: opportunity_vectors.db")

    # Load training data
    data_files = [
        ('detailed_opportunities.json', 'top_15_fast_money_makers'),
        ('strategic_monetization_report.json', None),
    ]

    total_trained = 0

    for filepath, key in data_files:
        path = Path(filepath)

        if not path.exists():
            print(f"⚠️  File not found: {filepath}")
            continue

        print(f"\n📖 Loading opportunities from {filepath}...")

        with open(path, 'r') as f:
            data = json.load(f)

        # Extract opportunities based on file structure
        if key and key in data:
            opportunities = data[key]
        elif isinstance(data, list):
            opportunities = data
        elif 'opportunities' in data:
            opportunities = data['opportunities']
        else:
            print(f"⚠️  Unknown file format: {filepath}")
            continue

        print(f"📊 Found {len(opportunities)} opportunities")

        # Train
        trained = train_from_opportunities(db, opportunities)
        total_trained += trained

        print(f"🎓 Training from {filepath} complete: {trained} stored")

    print(f"\n{'=' * 70}")
    print(f"🎉 TRAINING COMPLETE: {total_trained} opportunities stored")
    print(f"{'=' * 70}")

    # Validate
    if total_trained > 0:
        validate_training(db)
        extract_patterns(db)

    # Close database
    db.close()

    print(f"\n✅ Vector database saved: opportunity_vectors.db")
    print(f"   You can now use this for similarity search and pattern recognition!")
    print(f"\n💡 Next steps:")
    print(f"   1. Use the database to find similar repos")
    print(f"   2. Integrate with Rust system")
    print(f"   3. Build autonomous discovery")


if __name__ == '__main__':
    main()
