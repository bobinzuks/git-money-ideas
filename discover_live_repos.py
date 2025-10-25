#!/usr/bin/env python3
"""
Live GitHub Repository Discovery & Training

Fetches real repositories from GitHub and trains the vector database
on live data for immediate pattern learning.
"""

import json
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests

# Import our training module
from train_simple_vector_db import SimpleVectorDB, generate_embedding

class LiveGitHubDiscovery:
    """Discover and analyze live GitHub repositories"""

    def __init__(self, github_token: Optional[str] = None):
        self.token = github_token or os.getenv('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
        self.headers = {}

        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
            print(f"✅ Using GitHub token (authenticated - 5000 req/hour)")
        else:
            print(f"⚠️  No GitHub token (60 req/hour limit)")
            print(f"   Set GITHUB_TOKEN env var for higher limits")

        self.headers['Accept'] = 'application/vnd.github.v3+json'

    def search_repositories(
        self,
        query: str,
        sort: str = 'stars',
        min_stars: int = 100,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Search GitHub repositories"""

        print(f"\n🔍 Searching GitHub: {query}")
        print(f"   Min stars: {min_stars}, Max results: {max_results}")

        # Build search query
        search_query = f"{query} stars:>={min_stars}"

        url = f"{self.base_url}/search/repositories"
        params = {
            'q': search_query,
            'sort': sort,
            'order': 'desc',
            'per_page': min(100, max_results)
        }

        repos = []
        page = 1
        max_pages = (max_results // 100) + 1

        while len(repos) < max_results and page <= max_pages:
            params['page'] = page

            try:
                response = requests.get(url, headers=self.headers, params=params)

                # Check rate limit
                remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                if remaining < 10:
                    print(f"⚠️  Rate limit low: {remaining} requests remaining")

                response.raise_for_status()
                data = response.json()

                items = data.get('items', [])
                if not items:
                    break

                repos.extend(items)
                print(f"   Fetched page {page}: {len(items)} repos (total: {len(repos)})")

                page += 1
                time.sleep(1.2)  # Rate limiting

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print(f"❌ Rate limit exceeded. Wait or add GitHub token.")
                    break
                else:
                    print(f"❌ Error: {e}")
                    break

        print(f"✅ Found {len(repos)} repositories")
        return repos[:max_results]

    def get_trending_repos(self, language: str = '', days: int = 7) -> List[Dict[str, Any]]:
        """Get trending repositories"""

        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        query = f"created:>{since_date}"
        if language:
            query += f" language:{language}"

        return self.search_repositories(query, sort='stars', min_stars=50, max_results=30)

    def analyze_repository(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a repository for monetization potential"""

        # Basic metrics
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        watchers = repo.get('watchers_count', 0)
        open_issues = repo.get('open_issues_count', 0)
        language = repo.get('language', 'Unknown')
        description = repo.get('description', '')
        topics = repo.get('topics', [])

        # Activity score
        has_recent_push = False
        pushed_at = repo.get('pushed_at')
        if pushed_at:
            pushed_date = datetime.strptime(pushed_at, '%Y-%m-%dT%H:%M:%SZ')
            days_since_push = (datetime.now() - pushed_date).days
            has_recent_push = days_since_push < 30

        activity_score = (
            (1.0 if has_recent_push else 0.0) +
            (min(open_issues / 50.0, 1.0))
        )

        # Commercial keywords
        commercial_keywords = [
            'enterprise', 'saas', 'platform', 'api', 'sdk',
            'security', 'monitoring', 'analytics', 'automation',
            'ai', 'ml', 'llm', 'database', 'framework'
        ]

        text = f"{description} {' '.join(topics)}".lower()
        keyword_score = sum(1 for kw in commercial_keywords if kw in text)

        # Calculate commercial score (0-10)
        score = (
            min(stars / 1000.0, 3.0) +  # Max 3 points
            min(forks / 200.0, 2.0) +   # Max 2 points
            activity_score +             # Max 2 points
            min(keyword_score / 3.0, 2.0) +  # Max 2 points
            (1.0 if repo.get('has_wiki') else 0.0)  # 1 point
        )

        # Determine category
        category = self.categorize_repo(repo)

        # Estimate revenue potential
        revenue_estimate = self.estimate_revenue(stars, category)

        return {
            'rank': None,  # Will be set later
            'project': repo.get('name', 'Unknown'),
            'owner': {
                'username': repo.get('owner', {}).get('login', 'unknown'),
                'profile_url': repo.get('owner', {}).get('html_url', ''),
                'followers': None,  # Would need additional API call
                'company': None,
                'location': None,
            },
            'repository': {
                'name': repo.get('name', 'Unknown'),
                'url': repo.get('html_url', ''),
                'stars': stars,
                'forks': forks,
                'description': description or 'No description',
                'language': language,
                'category': category,
                'topics': topics,
            },
            'monetization': {
                'strategies': self.suggest_strategies(category),
                'revenue_potential_score': round(score, 1),
                'time_to_market': '2-6 months',
                'required_investment': f'${int(score * 10)}K-${int(score * 20)}K',
                'estimated_annual_revenue': revenue_estimate,
                'why_fast': self.why_fast(repo, category),
            },
        }

    def categorize_repo(self, repo: Dict[str, Any]) -> str:
        """Categorize repository based on content"""

        desc = (repo.get('description') or '').lower()
        topics = [t.lower() for t in repo.get('topics', [])]
        language = (repo.get('language') or '').lower()
        text = f"{desc} {' '.join(topics)}"

        # Category detection
        if any(kw in text for kw in ['security', 'pentest', 'vulnerability', 'exploit']):
            return 'Security Tools'
        elif any(kw in text for kw in ['ai', 'ml', 'machine learning', 'neural', 'llm', 'gpt']):
            return 'AI/ML Tools'
        elif any(kw in text for kw in ['devops', 'deployment', 'ci/cd', 'kubernetes', 'docker']):
            return 'DevOps Tools'
        elif any(kw in text for kw in ['api', 'framework', 'library', 'sdk']):
            return 'Developer Framework'
        elif any(kw in text for kw in ['dashboard', 'analytics', 'monitoring', 'observability']):
            return 'Analytics Platform'
        elif any(kw in text for kw in ['database', 'storage', 'sql', 'nosql']):
            return 'Database Technology'
        elif any(kw in text for kw in ['web', 'frontend', 'react', 'vue', 'angular']):
            return 'Web Development'
        elif any(kw in text for kw in ['education', 'tutorial', 'learning', 'course']):
            return 'Education Platform'
        else:
            return 'General Software'

    def suggest_strategies(self, category: str) -> List[str]:
        """Suggest monetization strategies based on category"""

        strategies = {
            'Security Tools': [
                'Enterprise License: $10K-100K/year',
                'Managed SaaS: $299-2,999/month',
                'Professional Services: $150-300/hour',
                'Training & Certification: $2K-5K per professional',
            ],
            'AI/ML Tools': [
                'API Access: $0.001-0.10 per request',
                'Enterprise License: $50K-500K/year',
                'Custom Model Training: $20K-200K per project',
                'Consulting Services: $200-500/hour',
            ],
            'DevOps Tools': [
                'SaaS Platform: $99-999/month per team',
                'Enterprise Support: $25K-100K/year',
                'Professional Services: $150-300/hour',
                'Training: $1K-3K per developer',
            ],
            'Developer Framework': [
                'Pro/Enterprise Tiers: $49-499/month',
                'Consulting: $150-350/hour',
                'Custom Development: $50K-300K per project',
                'Training Workshops: $2K-10K per session',
            ],
            'Analytics Platform': [
                'SaaS Subscriptions: $99-2,999/month',
                'Enterprise Licensing: $50K-500K/year',
                'White-Label Licensing: $100K-1M one-time',
                'Professional Services: $200-400/hour',
            ],
        }

        return strategies.get(category, [
            'Freemium SaaS: $29-299/month',
            'Enterprise License: $10K-100K/year',
            'Consulting Services: $150-300/hour',
            'Training & Support: $2K-10K',
        ])

    def estimate_revenue(self, stars: int, category: str) -> str:
        """Estimate revenue potential based on stars and category"""

        # Base multiplier by category
        multipliers = {
            'Security Tools': 150,
            'AI/ML Tools': 200,
            'DevOps Tools': 120,
            'Analytics Platform': 150,
            'Developer Framework': 100,
            'Database Technology': 180,
        }

        multiplier = multipliers.get(category, 80)

        # Estimate based on stars
        low = int(stars * multiplier * 0.1)
        high = int(stars * multiplier * 0.5)

        # Format as K or M
        if high >= 1_000_000:
            return f"${low // 1000}K-${high // 1_000_000}M"
        else:
            return f"${low // 1000}K-${high // 1000}K"

    def why_fast(self, repo: Dict[str, Any], category: str) -> str:
        """Explain why this is a fast money maker"""

        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)

        reasons = []

        if stars >= 1000:
            reasons.append('proven user demand')
        if forks >= 100:
            reasons.append('active community')
        if category in ['Security Tools', 'AI/ML Tools', 'DevOps Tools']:
            reasons.append('high-value enterprise market')

        if not reasons:
            reasons.append('emerging opportunity')

        return ', '.join(reasons).capitalize()


def main():
    """Main discovery pipeline"""

    print("=" * 70)
    print("🔍 LIVE GITHUB REPOSITORY DISCOVERY & TRAINING")
    print("=" * 70)

    # Initialize GitHub client
    github = LiveGitHubDiscovery()

    # Initialize vector database
    db = SimpleVectorDB("opportunity_vectors.db")
    print("\n✅ Vector database loaded")

    # Discovery queries
    queries = [
        ('security pentesting red team', 'Security'),
        ('ai machine learning llm', 'AI/ML'),
        ('devops kubernetes deployment automation', 'DevOps'),
        ('api framework sdk developer', 'Developer Tools'),
        ('analytics dashboard monitoring', 'Analytics'),
        ('database nosql storage', 'Database'),
    ]

    all_opportunities = []

    for query, category in queries:
        print(f"\n{'=' * 70}")
        print(f"Category: {category}")
        print(f"{'=' * 70}")

        repos = github.search_repositories(query, min_stars=500, max_results=20)

        for i, repo in enumerate(repos, 1):
            # Analyze repo
            opportunity = github.analyze_repository(repo)
            opportunity['rank'] = i

            all_opportunities.append(opportunity)

            # Train vector database
            combined_text = f"{opportunity['repository']['name']} " \
                           f"{opportunity['repository']['description']} " \
                           f"{opportunity['repository']['category']}"

            embedding = generate_embedding(combined_text)

            metadata = {
                'project': opportunity['project'],
                'owner': opportunity['owner']['username'],
                'stars': opportunity['repository']['stars'],
                'language': opportunity['repository']['language'],
                'category': opportunity['repository']['category'],
                'revenue_score': opportunity['monetization']['revenue_potential_score'],
                'estimated_revenue': opportunity['monetization']['estimated_annual_revenue'],
                'url': opportunity['repository']['url'],
                'discovered_at': datetime.now().isoformat(),
                'source': 'live_discovery',
            }

            db.store(
                f"{opportunity['owner']['username']}/{opportunity['project']}",
                embedding,
                metadata
            )

            # Print summary
            score = opportunity['monetization']['revenue_potential_score']
            stars = opportunity['repository']['stars']
            revenue = opportunity['monetization']['estimated_annual_revenue']

            print(f"  {i}. {opportunity['project']} ({stars:,} ⭐) - Score: {score}/10")
            print(f"     Category: {opportunity['repository']['category']}")
            print(f"     Revenue: {revenue}")

    db.close()

    # Save discoveries to JSON
    output_file = f"live_discoveries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, 'w') as f:
        json.dump({
            'discovery_date': datetime.now().isoformat(),
            'total_discovered': len(all_opportunities),
            'opportunities': all_opportunities,
        }, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"🎉 DISCOVERY COMPLETE!")
    print(f"{'=' * 70}")
    print(f"✅ Discovered: {len(all_opportunities)} opportunities")
    print(f"✅ Trained vector database with live data")
    print(f"✅ Saved to: {output_file}")

    # Statistics
    high_value = [o for o in all_opportunities if o['monetization']['revenue_potential_score'] >= 7.0]
    print(f"\n📊 Statistics:")
    print(f"   High-value (≥7.0): {len(high_value)}")
    print(f"   Avg score: {sum(o['monetization']['revenue_potential_score'] for o in all_opportunities) / len(all_opportunities):.1f}")

    # Top 5
    sorted_opps = sorted(all_opportunities, key=lambda x: x['monetization']['revenue_potential_score'], reverse=True)

    print(f"\n🏆 Top 5 Discoveries:")
    for i, opp in enumerate(sorted_opps[:5], 1):
        print(f"\n{i}. {opp['project']} ({opp['repository']['stars']:,} ⭐)")
        print(f"   Score: {opp['monetization']['revenue_potential_score']}/10")
        print(f"   Revenue: {opp['monetization']['estimated_annual_revenue']}")
        print(f"   Category: {opp['repository']['category']}")
        print(f"   URL: {opp['repository']['url']}")


if __name__ == '__main__':
    main()
