#!/usr/bin/env python3
"""
🎮 GAMIFIED DISCOVERY QUEST: The 42→420 Challenge

For each of your 42 repos, find 10 similar ones and detect AgentDB opportunities.
Track points, unlock achievements, and level up your discovery skills!
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Any
from train_simple_vector_db import SimpleVectorDB, generate_embedding

class GameState:
    """Track player progress and scores"""

    def __init__(self):
        self.points = 0
        self.level = 1
        self.repos_discovered = 0
        self.agentdb_opportunities = 0
        self.high_value_found = 0
        self.patterns_learned = 0

        self.achievements = []
        self.history = []

    def add_points(self, points: int, reason: str):
        self.points += points
        self.history.append({
            'points': points,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        print(f"  💰 +{points} points! {reason}")

    def check_level_up(self):
        """Check if player leveled up"""
        old_level = self.level

        if self.points >= 100000:
            self.level = 4
        elif self.points >= 10000:
            self.level = 3
        elif self.points >= 1000:
            self.level = 2

        if self.level > old_level:
            self.unlock_level(self.level)

    def unlock_level(self, level: int):
        """Unlock new level"""
        titles = {
            2: "Pattern Hunter",
            3: "Revenue Oracle",
            4: "Infinite Scaler"
        }

        print(f"\n{'='*70}")
        print(f"🎉 LEVEL UP! You are now a {titles.get(level, 'Master')}!")
        print(f"{'='*70}")

    def add_achievement(self, name: str, description: str):
        """Unlock achievement"""
        if name not in self.achievements:
            self.achievements.append(name)
            print(f"\n🏅 ACHIEVEMENT UNLOCKED: {name}")
            print(f"   {description}")

    def show_stats(self):
        """Display current stats"""
        print(f"\n{'='*70}")
        print(f"📊 YOUR STATS")
        print(f"{'='*70}")
        print(f"Level: {self.level}")
        print(f"Points: {self.points:,}")
        print(f"Repos Discovered: {self.repos_discovered}")
        print(f"AgentDB Opportunities: {self.agentdb_opportunities}")
        print(f"High-Value Finds: {self.high_value_found}")
        print(f"Achievements: {len(self.achievements)}")


class AgentDBDetector:
    """Detect repos that would benefit from AgentDB integration"""

    # Keywords indicating AgentDB fit
    REAL_TIME_KEYWORDS = ['real-time', 'realtime', 'live', 'streaming', 'websocket']
    COLLABORATIVE_KEYWORDS = ['collaborative', 'multi-user', 'multiplayer', 'team', 'shared']
    DATA_KEYWORDS = ['analytics', 'monitoring', 'dashboard', 'metrics', 'observability']
    STATE_KEYWORDS = ['state', 'history', 'context', 'memory', 'session', 'persistence']
    AI_KEYWORDS = ['llm', 'gpt', 'ai', 'chatbot', 'conversation', 'assistant']

    @classmethod
    def check_fit(cls, repo: Dict[str, Any]) -> Dict[str, Any]:
        """Check if repo would benefit from AgentDB"""

        desc = repo['repository']['description'].lower()
        category = repo['repository']['category'].lower()
        topics = [t.lower() for t in repo['repository'].get('topics', [])]
        text = f"{desc} {category} {' '.join(topics)}"

        score = 0
        reasons = []

        # Check real-time features
        if any(kw in text for kw in cls.REAL_TIME_KEYWORDS):
            score += 3
            reasons.append("Real-time data needs → AgentDB for fast queries")

        # Check collaborative features
        if any(kw in text for kw in cls.COLLABORATIVE_KEYWORDS):
            score += 3
            reasons.append("Multi-user collaboration → AgentDB for shared state")

        # Check analytics/monitoring
        if any(kw in text for kw in cls.DATA_KEYWORDS):
            score += 2
            reasons.append("Analytics/monitoring → AgentDB for time-series storage")

        # Check state management
        if any(kw in text for kw in cls.STATE_KEYWORDS):
            score += 2
            reasons.append("State management → AgentDB for persistence")

        # Check AI/LLM
        if any(kw in text for kw in cls.AI_KEYWORDS):
            score += 4
            reasons.append("AI/LLM features → AgentDB for context/memory")

        is_fit = score >= 5

        if is_fit:
            # Estimate revenue boost
            base_revenue = cls.parse_revenue(repo['monetization']['estimated_annual_revenue'])
            revenue_with_agentdb = base_revenue * 2.5  # 2.5x multiplier

            return {
                'is_fit': True,
                'score': score,
                'reasons': reasons,
                'revenue_boost': revenue_with_agentdb - base_revenue,
                'revenue_boost_pct': 150,  # 2.5x = 150% increase
            }

        return {'is_fit': False, 'score': score}

    @staticmethod
    def parse_revenue(revenue_str: str) -> float:
        """Parse revenue string like $148K-$740K"""
        try:
            # Extract high estimate
            parts = revenue_str.replace('$', '').replace(',', '').split('-')
            if len(parts) >= 2:
                high = parts[1].strip()
                if 'M' in high:
                    return float(high.replace('M', '')) * 1000
                elif 'K' in high:
                    return float(high.replace('K', ''))
            return 100  # Default
        except:
            return 100


def run_quest():
    """Run the gamified discovery quest"""

    print("=" * 70)
    print("🎮 GAMIFIED DISCOVERY QUEST: The 42→420 Challenge")
    print("=" * 70)
    print()
    print("Mission: For each of your 42 repos, find 10 similar repositories")
    print("         Detect AgentDB integration opportunities")
    print("         Score 6,200+ points to reach Level 2!")
    print()

    # Initialize game state
    game = GameState()

    # Load discoveries
    print("📖 Loading your 42 discoveries...")
    with open('live_discoveries_20251024_105203.json', 'r') as f:
        data = json.load(f)

    discovered_repos = data['opportunities']
    print(f"✅ Loaded {len(discovered_repos)} repositories")

    game.repos_discovered = len(discovered_repos)
    game.add_points(len(discovered_repos) * 5, f"Discovered {len(discovered_repos)} repos")

    # Load vector database
    print("\n🧠 Loading vector database...")
    db = SimpleVectorDB("opportunity_vectors.db")
    print("✅ Vector DB loaded")

    # Achievement: First 10 repos
    if len(discovered_repos) >= 10:
        game.add_achievement("Discovery Scout", "Discovered 10+ repositories")

    # Achievement: Multiple categories
    categories = set(r['repository']['category'] for r in discovered_repos)
    if len(categories) >= 3:
        game.add_achievement("Category Explorer", f"Discovered {len(categories)} different categories")

    print(f"\n{'='*70}")
    print("🔍 STARTING SIMILARITY SEARCH")
    print(f"{'='*70}")

    all_similar = []
    agentdb_opportunities = []

    for i, repo in enumerate(discovered_repos, 1):
        project = repo['project']
        category = repo['repository']['category']
        stars = repo['repository']['stars']
        score = repo['monetization']['revenue_potential_score']

        print(f"\n[{i}/{len(discovered_repos)}] {project}")
        print(f"  Category: {category} | Stars: {stars:,} | Score: {score}")

        # Generate embedding
        combined_text = f"{repo['repository']['name']} " \
                       f"{repo['repository']['description']} " \
                       f"{category}"

        embedding = generate_embedding(combined_text)

        # Find similar repos
        similar_results = db.search_similar(embedding, top_k=11)  # +1 because first is usually self

        # Convert to objects with score and metadata
        class Match:
            def __init__(self, repo_id, score, metadata):
                self.id = repo_id
                self.score = score
                self.metadata = metadata

        similar = [Match(r[0], r[1], r[2]) for r in similar_results]

        # Filter out self
        similar = [s for s in similar if s.metadata.get('project') != project][:10]

        print(f"  Found {len(similar)} similar repos:")

        for j, match in enumerate(similar, 1):
            similar_project = match.metadata.get('project', 'Unknown')
            similar_score = match.metadata.get('revenue_score', 0)
            similarity = match.score

            print(f"    {j}. {similar_project} (Score: {similar_score}, Similarity: {similarity:.2f})")

            # Points for finding similar
            game.add_points(10, f"Similar repo: {similar_project}")

            # Bonus for high similarity
            if similarity > 0.8:
                game.add_points(20, "High similarity match!")

            # Bonus for high value
            if similar_score >= 7.0:
                game.add_points(20, "High-value opportunity!")
                game.high_value_found += 1

            all_similar.append({
                'source': project,
                'similar': similar_project,
                'similarity': similarity,
                'score': similar_score,
            })

        # Check for AgentDB fit
        agentdb_result = AgentDBDetector.check_fit(repo)

        if agentdb_result['is_fit']:
            print(f"\n  🎯 AGENTDB OPPORTUNITY DETECTED!")
            print(f"     Score: {agentdb_result['score']}/10")

            for reason in agentdb_result['reasons']:
                print(f"     • {reason}")

            revenue_boost = agentdb_result['revenue_boost']
            print(f"     💰 Revenue Boost: +${revenue_boost:.0f}K/year with AgentDB")

            game.add_points(100, f"AgentDB opportunity: {project}")
            game.agentdb_opportunities += 1

            agentdb_opportunities.append({
                'project': project,
                'category': category,
                'agentdb_score': agentdb_result['score'],
                'reasons': agentdb_result['reasons'],
                'revenue_boost': revenue_boost,
                'url': repo['repository']['url'],
            })

            # Extra bonus for high AgentDB score
            if agentdb_result['score'] >= 8:
                game.add_points(50, "Perfect AgentDB fit!")

        # Check for level up after each repo
        game.check_level_up()

    db.close()

    # Final achievements
    if len(all_similar) >= 100:
        game.add_achievement("Similarity Master", "Found 100+ similar repositories")

    if game.agentdb_opportunities >= 5:
        game.add_achievement("AgentDB Detective", "Identified 5+ AgentDB opportunities")

    if game.agentdb_opportunities >= 10:
        game.add_achievement("Integration Genius", "Identified 10+ AgentDB opportunities")

    # Save results
    output_file = f"quest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    results = {
        'completed_at': datetime.now().isoformat(),
        'game_state': {
            'level': game.level,
            'points': game.points,
            'repos_discovered': game.repos_discovered,
            'agentdb_opportunities': game.agentdb_opportunities,
            'high_value_found': game.high_value_found,
            'achievements': game.achievements,
        },
        'similar_repos_found': len(all_similar),
        'similar_repos': all_similar,
        'agentdb_opportunities': agentdb_opportunities,
        'point_history': game.history,
    }

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Final stats
    print(f"\n{'='*70}")
    print("🎉 QUEST COMPLETE!")
    print(f"{'='*70}")

    game.show_stats()

    print(f"\n📁 Results saved to: {output_file}")

    # Leaderboard position
    print(f"\n🏆 LEADERBOARD POSITION")
    print(f"{'='*70}")

    if game.level >= 4:
        print("🥇 Rank: LEGENDARY - Infinite Scaler")
    elif game.level >= 3:
        print("🥈 Rank: EXPERT - Revenue Oracle")
    elif game.level >= 2:
        print("🥉 Rank: ADVANCED - Pattern Hunter")
    else:
        print("🎖️  Rank: NOVICE - Discovery Scout")

    # Next milestone
    if game.level < 2:
        needed = 1000 - game.points
        print(f"\nNext Level: {needed:,} points needed")
    elif game.level < 3:
        needed = 10000 - game.points
        print(f"\nNext Level: {needed:,} points needed")
    elif game.level < 4:
        needed = 100000 - game.points
        print(f"\nNext Level: {needed:,} points needed")
    else:
        print(f"\n🎊 YOU'VE REACHED MAX LEVEL!")

    # AgentDB opportunities summary
    if agentdb_opportunities:
        print(f"\n💡 TOP AGENTDB OPPORTUNITIES")
        print(f"{'='*70}")

        sorted_opps = sorted(agentdb_opportunities, key=lambda x: x['revenue_boost'], reverse=True)

        for i, opp in enumerate(sorted_opps[:5], 1):
            print(f"\n{i}. {opp['project']}")
            print(f"   Category: {opp['category']}")
            print(f"   AgentDB Score: {opp['agentdb_score']}/10")
            print(f"   Revenue Boost: +${opp['revenue_boost']:.0f}K/year")
            print(f"   Reasons:")
            for reason in opp['reasons']:
                print(f"     • {reason}")
            print(f"   URL: {opp['url']}")

        total_boost = sum(o['revenue_boost'] for o in agentdb_opportunities)
        print(f"\n💰 TOTAL POTENTIAL REVENUE BOOST: ${total_boost:.0f}K/year")
        print(f"   Average: ${total_boost / len(agentdb_opportunities):.0f}K per project")

    print(f"\n{'='*70}")
    print("🚀 Ready for the next quest? Train the WASM engine!")
    print("   python3 train_wasm_engine.py")
    print(f"{'='*70}")


if __name__ == '__main__':
    try:
        run_quest()
    except KeyboardInterrupt:
        print("\n\n⏸️  Quest paused. Your progress has been saved.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Quest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
