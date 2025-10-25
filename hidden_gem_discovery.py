#!/usr/bin/env python3
"""
💎 Hidden Gem Discovery - Find Low-Traction, High-AgentDB-Potential Repos

Strategy: Ignore stars/popularity. Find repos that become 50x more valuable with AgentDB.

Scoring factors:
1. LOW validation (< 500 stars) - undiscovered
2. HIGH AgentDB fit (real-time, multi-user, state management)
3. CLEAR pain point (something people actually need)
4. SIMPLE to add AgentDB (not complex rewrite)
5. NOVEL idea potential (unique angle)
"""

import json
import requests
import time
from datetime import datetime
from typing import List, Dict, Any
from collections import Counter

class HiddenGemScorer:
    """
    Score repos for hidden gem potential with AgentDB

    Traditional scoring: High stars = high value
    Hidden gem scoring: Low stars + High AgentDB multiplier = 50x opportunity
    """

    # Keywords indicating AgentDB creates massive value
    AGENTDB_MULTIPLIER_KEYWORDS = {
        'realtime': 10.0,       # Real-time apps get 10x better with AgentDB
        'collaborative': 15.0,  # Collaboration needs shared state
        'multiplayer': 15.0,    # Multi-user = AgentDB goldmine
        'chat': 12.0,           # Chat needs message history
        'dashboard': 8.0,       # Dashboards need time-series data
        'analytics': 8.0,       # Analytics = perfect AgentDB use case
        'monitoring': 8.0,      # Monitoring needs fast queries
        'memory': 20.0,         # AI memory = AgentDB core use case
        'context': 15.0,        # Context storage = AgentDB
        'history': 10.0,        # History tracking = AgentDB
        'state': 12.0,          # State management = AgentDB
        'sync': 15.0,           # Sync between users/devices
        'live': 10.0,           # Live updates
        'streaming': 8.0,       # Streaming data
        'websocket': 8.0,       # WebSocket = real-time
        'feed': 7.0,            # Activity feeds
        'notification': 7.0,    # Notification systems
        'session': 10.0,        # Session management
        'cache': 6.0,           # Caching layer
        'queue': 6.0,           # Message queues
    }

    # Novel idea indicators
    NOVELTY_KEYWORDS = [
        'new', 'novel', 'innovative', 'unique', 'different',
        'experimental', 'prototype', 'proof-of-concept', 'poc',
        'exploration', 'research', 'fresh', 'alternative'
    ]

    @classmethod
    def score_hidden_gem(cls, repo: Dict[str, Any]) -> Dict[str, Any]:
        """Score a repo for hidden gem + AgentDB potential"""

        stars = repo.get('stars', 0)
        forks = repo.get('forks', 0)
        description = (repo.get('description') or '').lower()
        topics = [t.lower() for t in repo.get('topics', [])]
        category = (repo.get('category') or '').lower()
        language = (repo.get('language') or '').lower()

        text = f"{description} {' '.join(topics)} {category}"

        # Score components
        undiscovered_score = 0.0
        agentdb_multiplier = 1.0
        pain_point_score = 0.0
        simplicity_score = 0.0
        novelty_score = 0.0

        # 1. UNDISCOVERED SCORE (0-3 points)
        # Lower stars = more undiscovered
        if stars < 50:
            undiscovered_score = 3.0      # Almost nobody knows about it
        elif stars < 100:
            undiscovered_score = 2.5
        elif stars < 250:
            undiscovered_score = 2.0
        elif stars < 500:
            undiscovered_score = 1.5
        else:
            undiscovered_score = 0.0      # Already discovered

        # Bonus: Has activity but low stars = under-the-radar gem
        if forks > 0 and stars < 100:
            undiscovered_score += 1.0

        # 2. AGENTDB MULTIPLIER (1x - 50x)
        # How much more valuable does it become with AgentDB?
        multiplier_scores = []

        for keyword, mult in cls.AGENTDB_MULTIPLIER_KEYWORDS.items():
            if keyword in text:
                multiplier_scores.append(mult)

        # Compound multipliers (multiple matches = exponential value)
        if multiplier_scores:
            # Average of top 3 multipliers
            top_3 = sorted(multiplier_scores, reverse=True)[:3]
            agentdb_multiplier = sum(top_3) / len(top_3)

            # Bonus for multiple matches
            if len(multiplier_scores) >= 3:
                agentdb_multiplier *= 1.5  # Compound effect

            # Cap at 50x
            agentdb_multiplier = min(agentdb_multiplier, 50.0)

        # 3. PAIN POINT SCORE (0-2 points)
        # Does it solve a real problem?
        pain_indicators = [
            'problem', 'solution', 'fix', 'simplify', 'easier',
            'better', 'improve', 'manage', 'organize', 'track',
            'automate', 'faster', 'efficient', 'productivity'
        ]

        pain_point_score = sum(1.0 for word in pain_indicators if word in text)
        pain_point_score = min(pain_point_score * 0.5, 2.0)

        # 4. SIMPLICITY SCORE (0-2 points)
        # How easy is it to add AgentDB?
        simple_indicators = [
            'simple', 'minimal', 'lightweight', 'small', 'basic',
            'starter', 'boilerplate', 'template', 'example'
        ]

        simplicity_score = sum(1.0 for word in simple_indicators if word in text)
        simplicity_score = min(simplicity_score * 0.5, 2.0)

        # Bonus: Simple languages/frameworks
        if language in ['javascript', 'typescript', 'python', 'go']:
            simplicity_score += 0.5

        # 5. NOVELTY SCORE (0-3 points)
        # Is this a new/unique idea?
        novelty_score = sum(1.0 for word in cls.NOVELTY_KEYWORDS if word in text)
        novelty_score = min(novelty_score * 0.5, 3.0)

        # Recent creation = more novel
        created_at = repo.get('created_at')
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (datetime.now(created_date.tzinfo) - created_date).days

                if days_old < 180:  # Less than 6 months
                    novelty_score += 1.5
                elif days_old < 365:  # Less than 1 year
                    novelty_score += 1.0
            except:
                pass

        # Calculate final scores
        base_score = (
            undiscovered_score +
            pain_point_score +
            simplicity_score +
            novelty_score
        )

        # Hidden gem score = base * AgentDB multiplier
        hidden_gem_score = base_score * (agentdb_multiplier / 10.0)

        # Estimate value transformation
        base_value = max(stars * 50, 1000)  # Minimum $1K base value
        value_with_agentdb = base_value * agentdb_multiplier

        return {
            'hidden_gem_score': round(hidden_gem_score, 2),
            'undiscovered_score': round(undiscovered_score, 1),
            'agentdb_multiplier': round(agentdb_multiplier, 1),
            'pain_point_score': round(pain_point_score, 1),
            'simplicity_score': round(simplicity_score, 1),
            'novelty_score': round(novelty_score, 1),
            'base_value': f"${int(base_value/1000)}K",
            'value_with_agentdb': f"${int(value_with_agentdb/1000)}K",
            'value_increase': f"{int(agentdb_multiplier)}x",
            'is_hidden_gem': hidden_gem_score >= 10.0 and stars < 500,
            'multiplier_reasons': [
                kw for kw in cls.AGENTDB_MULTIPLIER_KEYWORDS.keys()
                if kw in text
            ]
        }


class HiddenGemDiscovery:
    """Discover hidden gems from GitHub"""

    def __init__(self, github_token: str = None):
        self.token = github_token
        self.headers = {}
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
        self.headers['Accept'] = 'application/vnd.github.v3+json'

    def find_hidden_gems(self, max_stars: int = 500, count: int = 100) -> List[Dict]:
        """
        Find hidden gems: low stars, high AgentDB potential

        Strategy:
        1. Search for AgentDB-friendly keywords
        2. Filter: stars < max_stars (undiscovered)
        3. Score for AgentDB multiplier potential
        4. Return top gems
        """

        print(f"🔍 Searching for hidden gems (max {max_stars} stars)...")

        # Search queries optimized for AgentDB multipliers
        queries = [
            'realtime stars:<500',
            'collaborative stars:<500',
            'multiplayer stars:<500',
            'chat memory stars:<500',
            'dashboard analytics stars:<500',
            'state management stars:<500',
            'live streaming stars:<500',
            'websocket real-time stars:<500',
        ]

        all_repos = []
        seen_urls = set()

        for query in queries:
            print(f"  Searching: {query}")

            repos = self._search_repos(query, max_results=20)

            for repo in repos:
                url = repo.get('html_url')
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_repos.append(repo)

            if len(all_repos) >= count:
                break

            time.sleep(1.2)

        print(f"✅ Found {len(all_repos)} potential gems")

        # Score each repo
        gems = []
        for repo in all_repos:
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
                'category': self._categorize(repo),
            }

            score_data = HiddenGemScorer.score_hidden_gem(repo_data)

            if score_data['is_hidden_gem']:
                gems.append({
                    **repo_data,
                    **score_data
                })

        # Sort by hidden gem score
        gems.sort(key=lambda x: x['hidden_gem_score'], reverse=True)

        return gems[:count]

    def _search_repos(self, query: str, max_results: int = 20, page: int = 1) -> List[Dict]:
        """Search GitHub with pagination support"""
        url = "https://api.github.com/search/repositories"
        params = {
            'q': query,
            'sort': 'updated',  # Recently updated = active
            'order': 'desc',
            'per_page': max_results,
            'page': page
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('items', [])
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            return []

    def _categorize(self, repo: Dict) -> str:
        """Categorize repo"""
        desc = (repo.get('description') or '').lower()
        topics = [t.lower() for t in repo.get('topics', [])]
        text = f"{desc} {' '.join(topics)}"

        if any(kw in text for kw in ['chat', 'message', 'conversation']):
            return 'Communication'
        elif any(kw in text for kw in ['dashboard', 'analytics', 'monitoring']):
            return 'Analytics'
        elif any(kw in text for kw in ['collaborative', 'multiplayer', 'team']):
            return 'Collaboration'
        elif any(kw in text for kw in ['realtime', 'live', 'streaming']):
            return 'Real-time'
        elif any(kw in text for kw in ['ai', 'ml', 'llm', 'gpt']):
            return 'AI/ML'
        else:
            return 'General'


def main():
    """Demo: Find hidden gems"""

    print("=" * 70)
    print("💎 HIDDEN GEM DISCOVERY - AgentDB 50x Multiplier")
    print("=" * 70)
    print()

    discovery = HiddenGemDiscovery()

    # Find hidden gems
    gems = discovery.find_hidden_gems(max_stars=500, count=20)

    print(f"\n{'='*70}")
    print(f"💎 TOP {len(gems)} HIDDEN GEMS")
    print(f"{'='*70}\n")

    for i, gem in enumerate(gems, 1):
        print(f"{i}. {gem['name']} by {gem['owner']}")
        print(f"   ⭐ Stars: {gem['stars']} (UNDISCOVERED)")
        print(f"   📊 Hidden Gem Score: {gem['hidden_gem_score']}/10")
        print(f"   🚀 AgentDB Multiplier: {gem['agentdb_multiplier']}x")
        print(f"   💰 Value: {gem['base_value']} → {gem['value_with_agentdb']} ({gem['value_increase']} increase)")
        print(f"   🎯 Why: {', '.join(gem['multiplier_reasons'][:3])}")
        print(f"   🔗 {gem['url']}")
        print()

    # Save results
    output_file = f"hidden_gems_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'discovered_at': datetime.now().isoformat(),
            'total_gems': len(gems),
            'gems': gems
        }, f, indent=2)

    print(f"✅ Saved to: {output_file}")

    # Statistics
    avg_multiplier = sum(g['agentdb_multiplier'] for g in gems) / len(gems)
    avg_stars = sum(g['stars'] for g in gems) / len(gems)

    print(f"\n📊 Statistics:")
    print(f"   Average AgentDB Multiplier: {avg_multiplier:.1f}x")
    print(f"   Average Stars: {avg_stars:.0f} (truly hidden!)")
    print(f"   Hidden Gems (score ≥10): {len(gems)}")


if __name__ == '__main__':
    main()
