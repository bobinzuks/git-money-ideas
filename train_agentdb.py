#!/usr/bin/env python3
"""
AgentDB Training Script - Trains AgentDB on existing opportunity data

This script:
1. Starts AgentDB server
2. Loads opportunities from JSON files
3. Generates embeddings using simple text features
4. Stores in AgentDB for pattern learning
5. Validates training quality
"""

import json
import subprocess
import time
import requests
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import signal
import sys

AGENTDB_PORT = 8765
AGENTDB_URL = f"http://localhost:{AGENTDB_PORT}"

def generate_simple_embedding(text: str, dim: int = 128) -> List[float]:
    """
    Generate a simple embedding based on text features.
    In production, use sentence-transformers or similar.
    """
    embedding = np.zeros(dim, dtype=np.float32)

    # Basic text statistics
    words = text.lower().split()
    char_count = len(text)
    word_count = len(words)

    # Dimension 0-9: Basic features
    embedding[0] = min(char_count / 1000.0, 1.0)
    embedding[1] = min(word_count / 100.0, 1.0)
    embedding[2] = 0.8 if 'ai' in text.lower() or 'ml' in text.lower() else 0.0
    embedding[3] = 0.8 if 'security' in text.lower() or 'cyber' in text.lower() else 0.0
    embedding[4] = 0.7 if 'platform' in text.lower() or 'service' in text.lower() else 0.0
    embedding[5] = 0.7 if 'api' in text.lower() or 'sdk' in text.lower() else 0.0
    embedding[6] = 0.9 if 'enterprise' in text.lower() else 0.0
    embedding[7] = 0.8 if 'saas' in text.lower() or 'cloud' in text.lower() else 0.0
    embedding[8] = 0.7 if 'developer' in text.lower() or 'devops' in text.lower() else 0.0
    embedding[9] = 0.7 if 'analytics' in text.lower() or 'monitoring' in text.lower() else 0.0

    # Dimension 10+: Keyword features
    keywords = [
        'python', 'javascript', 'go', 'rust', 'java',
        'api', 'framework', 'library', 'tool', 'platform',
        'security', 'authentication', 'encryption', 'privacy',
        'ai', 'ml', 'llm', 'gpt', 'neural',
        'database', 'sql', 'nosql', 'redis', 'postgres',
        'web', 'mobile', 'desktop', 'cli', 'gui',
        'devops', 'cicd', 'kubernetes', 'docker', 'cloud',
        'monitoring', 'logging', 'analytics', 'metrics',
        'automation', 'testing', 'deployment', 'integration',
    ]

    for i, keyword in enumerate(keywords):
        if i + 10 < dim:
            embedding[i + 10] = 0.5 if keyword in text.lower() else 0.0

    # Normalize
    magnitude = np.linalg.norm(embedding)
    if magnitude > 0:
        embedding = embedding / magnitude

    return embedding.tolist()

def start_agentdb_server():
    """Start AgentDB server in background"""
    print(f"🧠 Starting AgentDB server on port {AGENTDB_PORT}...")

    process = subprocess.Popen(
        ['npx', 'agentdb', 'serve', '--port', str(AGENTDB_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
    )

    # Wait for server to start
    print("⏳ Waiting for AgentDB to start...")
    for i in range(10):
        time.sleep(1)
        try:
            response = requests.get(f"{AGENTDB_URL}/health", timeout=1)
            if response.status_code == 200:
                print("✅ AgentDB server started successfully")
                return process
        except:
            print(f"   Attempt {i+1}/10...")

    print("❌ Failed to start AgentDB server")
    process.kill()
    sys.exit(1)

def store_opportunity(opportunity: Dict[str, Any]):
    """Store a single opportunity in AgentDB"""

    # Generate combined text for embedding
    repo_info = opportunity.get('repository', {})
    mon_info = opportunity.get('monetization', {})
    owner_info = opportunity.get('owner', {})
    market_info = opportunity.get('market_analysis', {})

    combined_text = f"{repo_info.get('name', '')} {repo_info.get('description', '')} " \
                   f"{repo_info.get('category', '')} {repo_info.get('language', '')} " \
                   f"{mon_info.get('why_fast', '')} {' '.join(mon_info.get('strategies', []))}"

    # Generate embedding
    embedding = generate_simple_embedding(combined_text)

    # Prepare metadata
    metadata = {
        'project': opportunity.get('project', ''),
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

    # Store in AgentDB
    repo_id = f"{owner_info.get('username', 'unknown')}/{repo_info.get('name', 'unknown')}"

    response = requests.post(
        f"{AGENTDB_URL}/api/vectors/store",
        json={
            'id': repo_id,
            'vector': embedding,
            'metadata': metadata
        },
        timeout=10
    )

    response.raise_for_status()
    return repo_id

def train_from_file(filepath: Path):
    """Load opportunities from JSON file and train AgentDB"""

    print(f"\n📖 Loading opportunities from {filepath.name}...")

    with open(filepath, 'r') as f:
        data = json.load(f)

    opportunities = []

    # Handle different file formats
    if 'top_15_fast_money_makers' in data:
        opportunities = data['top_15_fast_money_makers']
    elif isinstance(data, list):
        opportunities = data
    else:
        print(f"⚠️  Unknown file format: {filepath.name}")
        return 0

    print(f"📊 Found {len(opportunities)} opportunities to train on")

    success_count = 0
    error_count = 0

    for i, opp in enumerate(opportunities, 1):
        try:
            repo_id = store_opportunity(opp)
            success_count += 1

            if success_count % 5 == 0:
                print(f"✅ Stored {success_count}/{len(opportunities)}: {repo_id}")

        except Exception as e:
            error_count += 1
            print(f"❌ Error storing opportunity {i}: {e}")

    print(f"\n🎓 Training from {filepath.name} complete:")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Errors: {error_count}")

    return success_count

def validate_training():
    """Test similarity search to validate training"""
    print("\n🧪 Validating training quality...")

    # Test query: Find security tools
    test_text = "security platform for enterprise red team testing"
    test_embedding = generate_simple_embedding(test_text)

    response = requests.post(
        f"{AGENTDB_URL}/api/vectors/search",
        json={
            'vector': test_embedding,
            'top_k': 5,
            'filters': None
        },
        timeout=10
    )

    response.raise_for_status()
    results = response.json()

    print(f"\n🔍 Test Query: '{test_text}'")
    print(f"📊 Top 5 Similar Opportunities:")

    for i, result in enumerate(results[:5], 1):
        metadata = result.get('metadata', {})
        print(f"\n{i}. {metadata.get('project', 'Unknown')} (Score: {result.get('score', 0):.3f})")
        print(f"   Category: {metadata.get('category', 'N/A')}")
        print(f"   Revenue Score: {metadata.get('revenue_score', 0)}/10")
        print(f"   Estimated Revenue: {metadata.get('estimated_revenue', 'N/A')}")

    return True

def main():
    """Main training pipeline"""

    print("=" * 70)
    print("🎓 AGENTDB TRAINING PIPELINE")
    print("=" * 70)

    # Start AgentDB server
    agentdb_process = start_agentdb_server()

    try:
        # Find training data files
        data_files = [
            Path('detailed_opportunities.json'),
            Path('strategic_monetization_report.json'),
        ]

        total_trained = 0

        for filepath in data_files:
            if filepath.exists():
                trained = train_from_file(filepath)
                total_trained += trained
            else:
                print(f"⚠️  File not found: {filepath}")

        print(f"\n{'=' * 70}")
        print(f"🎉 TRAINING COMPLETE: {total_trained} opportunities stored in AgentDB")
        print(f"{'=' * 70}")

        # Validate training
        if total_trained > 0:
            validate_training()

        print("\n✅ AgentDB is now trained on your opportunities!")
        print(f"   Server running at: {AGENTDB_URL}")
        print(f"   You can now use the Rust system for intelligent discovery")
        print(f"\n💡 Press Ctrl+C to stop the server")

        # Keep server running
        try:
            agentdb_process.wait()
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down AgentDB server...")

    finally:
        # Clean up
        agentdb_process.terminate()
        agentdb_process.wait(timeout=5)
        print("✅ AgentDB server stopped")

if __name__ == '__main__':
    main()
