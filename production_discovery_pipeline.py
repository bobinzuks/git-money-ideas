#!/usr/bin/env python3
"""
🚀 PRODUCTION DISCOVERY PIPELINE - Full Scale

Process all 42 existing repos + discover 100+ new ones
with advanced embeddings and fast-money scoring
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from advanced_discovery_engine import (
    AdvancedEmbedding,
    FastMoneyScorer,
    MultiSourceDiscovery,
    AdvancedVectorDB
)

def process_existing_repos():
    """Process all 42 existing discoveries with new engine"""

    print("=" * 70)
    print("🔄 PROCESSING EXISTING 42 REPOS WITH ADVANCED ENGINE")
    print("=" * 70)

    # Load existing discoveries
    with open('live_discoveries_20251024_105203.json', 'r') as f:
        data = json.load(f)

    repos = data['opportunities']
    db = AdvancedVectorDB("advanced_vectors.db")

    processed = []
    improvements = []

    for i, repo in enumerate(repos, 1):
        project = repo['project']
        old_score = repo['monetization']['revenue_potential_score']

        # Prepare repo data
        repo_data = {
            'name': repo['repository']['name'],
            'description': repo['repository']['description'],
            'category': repo['repository']['category'],
            'topics': repo['repository'].get('topics', []),
            'language': repo['repository'].get('language'),
            'stars': repo['repository']['stars'],
            'forks': repo['repository']['forks'],
            'recent_activity': True,  # Assume active
        }

        # Generate advanced embedding
        embedding = AdvancedEmbedding.generate(repo_data)

        # Calculate new fast-money score
        score_data = FastMoneyScorer.score(repo_data)
        new_score = score_data['total_score']

        # Track improvement
        score_diff = new_score - old_score
        improvements.append({
            'project': project,
            'old_score': old_score,
            'new_score': new_score,
            'improvement': score_diff,
        })

        # Store in advanced DB
        metadata = {
            'project': project,
            'owner': repo['owner']['username'],
            'url': repo['repository']['url'],
            'category': repo_data['category'],
            'stars': repo_data['stars'],
            'forks': repo_data['forks'],
            'language': repo_data['language'],
            'fast_money_score': new_score,
            'revenue_estimate': score_data['estimated_revenue'],
            'time_to_market': score_data['time_to_market'],
            'risk_level': score_data['risk_level'],
            'old_score': old_score,
        }

        db.store(
            f"{repo['owner']['username']}/{project}",
            embedding,
            metadata
        )

        processed.append(metadata)

        # Show progress every 10
        if i % 10 == 0:
            print(f"  ✅ Processed {i}/{len(repos)} repos...")

    print(f"\n✅ Processed all {len(repos)} repos!")

    # Analyze improvements
    improvements.sort(key=lambda x: x['improvement'], reverse=True)

    print(f"\n{'='*70}")
    print("📊 SCORING IMPROVEMENTS - Top 10")
    print(f"{'='*70}")

    for i, imp in enumerate(improvements[:10], 1):
        sign = "+" if imp['improvement'] > 0 else ""
        print(f"{i:2d}. {imp['project']:<30} "
              f"Old: {imp['old_score']:.1f} → New: {imp['new_score']:.1f} "
              f"({sign}{imp['improvement']:.1f})")

    # Show biggest downgrades too
    print(f"\n📉 Biggest Score Reductions:")
    for i, imp in enumerate(improvements[-5:], 1):
        print(f"  {imp['project']:<30} "
              f"Old: {imp['old_score']:.1f} → New: {imp['new_score']:.1f} "
              f"({imp['improvement']:.1f})")

    # Stats
    avg_improvement = sum(i['improvement'] for i in improvements) / len(improvements)
    print(f"\n📈 Average Score Change: {avg_improvement:+.2f}")

    db.close()

    return processed


def discover_new_repos(count_target: int = 100):
    """Discover new repositories from multiple sources"""

    print(f"\n{'='*70}")
    print(f"🔍 DISCOVERING NEW REPOSITORIES (Target: {count_target})")
    print(f"{'='*70}")

    discovery = MultiSourceDiscovery()
    db = AdvancedVectorDB("advanced_vectors.db")

    all_discoveries = []

    # Strategy 1: Trending repos
    print("\n1. Trending Repositories...")
    trending = discovery.discover_trending(language='', since='weekly')
    print(f"   Found {len(trending)} trending repos")

    for repo in trending:
        processed = process_github_repo(repo, db)
        if processed:
            all_discoveries.append(processed)

    # Strategy 2: Topic-based discovery
    print("\n2. Topic-Based Discovery...")
    topics = [
        'security-tools', 'pentesting', 'red-team',
        'machine-learning', 'llm', 'ai',
        'devops', 'kubernetes', 'monitoring',
        'developer-tools', 'framework', 'api'
    ]

    for topic in topics:
        print(f"   Searching topic: {topic}...")
        repos = discovery.discover_by_topic(topic, min_stars=200)

        for repo in repos:
            processed = process_github_repo(repo, db)
            if processed:
                all_discoveries.append(processed)

        if len(all_discoveries) >= count_target:
            break

    # Remove duplicates
    seen = set()
    unique_discoveries = []
    for disc in all_discoveries:
        if disc['url'] not in seen:
            seen.add(disc['url'])
            unique_discoveries.append(disc)

    print(f"\n✅ Discovered {len(unique_discoveries)} new repositories!")

    db.close()

    return unique_discoveries


def process_github_repo(repo: Dict, db: AdvancedVectorDB) -> Optional[Dict]:
    """Process a GitHub API repo response"""

    try:
        repo_data = {
            'name': repo.get('name', ''),
            'description': repo.get('description'),
            'category': categorize_repo(repo),
            'topics': repo.get('topics', []),
            'language': repo.get('language'),
            'stars': repo.get('stargazers_count', 0),
            'forks': repo.get('forks_count', 0),
            'recent_activity': True,  # Would need to check pushed_at
        }

        # Generate embedding
        embedding = AdvancedEmbedding.generate(repo_data)

        # Score
        score_data = FastMoneyScorer.score(repo_data)

        # Only store if score >= 6.0
        if score_data['total_score'] < 6.0:
            return None

        # Prepare metadata
        metadata = {
            'project': repo.get('name'),
            'owner': repo.get('owner', {}).get('login', 'unknown'),
            'url': repo.get('html_url'),
            'category': repo_data['category'],
            'stars': repo_data['stars'],
            'forks': repo_data['forks'],
            'language': repo_data['language'],
            'fast_money_score': score_data['total_score'],
            'revenue_estimate': score_data['estimated_revenue'],
            'time_to_market': score_data['time_to_market'],
            'risk_level': score_data['risk_level'],
        }

        # Store
        repo_id = f"{metadata['owner']}/{metadata['project']}"
        db.store(repo_id, embedding, metadata)

        return metadata

    except Exception as e:
        print(f"    ⚠️  Error processing repo: {e}")
        return None


def categorize_repo(repo: Dict) -> str:
    """Categorize GitHub repo"""

    desc = (repo.get('description') or '').lower()
    topics = [t.lower() for t in repo.get('topics', [])]
    text = f"{desc} {' '.join(topics)}"

    if any(kw in text for kw in ['security', 'pentest', 'vulnerability']):
        return 'Security Tools'
    elif any(kw in text for kw in ['ai', 'ml', 'machine learning', 'llm']):
        return 'AI/ML Tools'
    elif any(kw in text for kw in ['devops', 'kubernetes', 'deployment']):
        return 'DevOps Tools'
    elif any(kw in text for kw in ['api', 'framework', 'library']):
        return 'Developer Framework'
    elif any(kw in text for kw in ['analytics', 'dashboard', 'monitoring']):
        return 'Analytics Platform'
    elif any(kw in text for kw in ['database', 'storage', 'sql']):
        return 'Database Technology'
    else:
        return 'General Software'


def generate_final_report():
    """Generate comprehensive report with all findings"""

    print(f"\n{'='*70}")
    print("📊 GENERATING FINAL REPORT")
    print(f"{'='*70}")

    db = AdvancedVectorDB("advanced_vectors.db")

    # Get statistics
    stats = db.get_stats()

    # Get top opportunities
    top_fast_money = db.get_top_fast_money(limit=20)

    print(f"\n✅ Database Statistics:")
    print(f"   Total Repositories: {stats['total_repos']}")
    print(f"   Average Score: {stats['avg_score']}")
    print(f"   Max Score: {stats['max_score']}")
    print(f"   Fast-Money Opportunities (≥7.0): {stats['fast_money_count']}")

    print(f"\n🏆 TOP 20 FAST-MONEY OPPORTUNITIES:")
    print(f"{'='*70}")

    for i, opp in enumerate(top_fast_money, 1):
        print(f"\n{i:2d}. {opp['project']} by {opp['owner']}")
        print(f"    Category: {opp['category']}")
        print(f"    Stars: {opp['stars']:,} | Language: {opp.get('language', 'N/A')}")
        print(f"    Score: {opp['fast_money_score']:.1f}/10")
        print(f"    Revenue: {opp['revenue_estimate']}")
        print(f"    Time: {opp['time_to_market']} | Risk: {opp['risk_level']}")
        print(f"    URL: {opp['url']}")

        # Show if improved from old score
        if 'old_score' in opp:
            diff = opp['fast_money_score'] - opp['old_score']
            if diff != 0:
                sign = "+" if diff > 0 else ""
                print(f"    📈 Score Improvement: {sign}{diff:.1f}")

    # Save to JSON
    output_file = f"production_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    report = {
        'generated_at': datetime.now().isoformat(),
        'statistics': stats,
        'top_opportunities': top_fast_money,
        'methodology': {
            'embedding_dimension': 256,
            'features': [
                'Category signals (10 features)',
                'Monetization keywords (10 features)',
                'TF-IDF word importance (10 features)',
                'Repository metrics (10 features)',
                'Language ecosystem signals',
                'Topic embeddings',
                'Character n-grams',
                'Word embeddings (100 features)'
            ],
            'scoring_factors': [
                'Market demand (stars, activity, community)',
                'Competition analysis',
                'Ease of monetization (category, keywords)',
                'Revenue potential (language, B2B market)'
            ]
        }
    }

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Report saved to: {output_file}")

    db.close()

    return report


def main():
    """Run full production pipeline"""

    print("=" * 70)
    print("🚀 PRODUCTION DISCOVERY PIPELINE")
    print("=" * 70)
    print()
    print("This pipeline will:")
    print("  1. Reprocess 42 existing repos with advanced scoring")
    print("  2. Discover 100+ new repositories")
    print("  3. Generate comprehensive report")
    print()

    try:
        # Step 1: Process existing
        existing = process_existing_repos()

        # Step 2: Discover new
        new_repos = discover_new_repos(count_target=100)

        # Step 3: Generate report
        report = generate_final_report()

        print(f"\n{'='*70}")
        print("🎉 PIPELINE COMPLETE!")
        print(f"{'='*70}")
        print(f"✅ Existing repos processed: {len(existing)}")
        print(f"✅ New repos discovered: {len(new_repos)}")
        print(f"✅ Total fast-money opportunities: {report['statistics']['fast_money_count']}")

        # Summary insights
        print(f"\n💡 KEY INSIGHTS:")
        print(f"   • Average score: {report['statistics']['avg_score']}/10")
        print(f"   • Best opportunity: {report['top_opportunities'][0]['project']}")
        print(f"   • Score: {report['top_opportunities'][0]['fast_money_score']:.1f}/10")
        print(f"   • Revenue: {report['top_opportunities'][0]['revenue_estimate']}")

    except KeyboardInterrupt:
        print("\n\n⏸️  Pipeline interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
