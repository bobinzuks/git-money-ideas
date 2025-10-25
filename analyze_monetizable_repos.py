#!/usr/bin/env python3
"""
Analyze GitHub stargazers' repositories for monetization opportunities.
"""

import json
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys

# GitHub API configuration
GITHUB_TOKEN = None  # Will use public API with rate limiting
HEADERS = {
    'Accept': 'application/vnd.github.v3+json',
}

# Monetization keywords indicating commercial potential
MONETIZATION_KEYWORDS = [
    'api', 'saas', 'platform', 'service', 'tool', 'framework',
    'ai', 'ml', 'machine-learning', 'llm', 'gpt', 'chatbot',
    'analytics', 'dashboard', 'admin', 'automation', 'deploy',
    'cloud', 'serverless', 'microservice', 'devops', 'cicd',
    'database', 'orm', 'cms', 'ecommerce', 'payment',
    'auth', 'authentication', 'security', 'monitoring'
]

# Low commercial value keywords (experiments, learning)
EXPERIMENTAL_KEYWORDS = [
    'tutorial', 'learning', 'example', 'demo', 'test', 'practice',
    'homework', 'course', 'exercise', 'sample', 'playground',
    'hello-world', 'getting-started', 'leetcode', 'interview'
]

def load_stargazers(filepath: str) -> List[Dict]:
    """Load stargazers data from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def filter_qualified_users(stargazers: List[Dict]) -> List[Dict]:
    """Filter users matching criteria: 50+ repos, 100+ followers."""
    return [
        user for user in stargazers
        if user.get('public_repos_count', 0) >= 50
        and user.get('followers', 0) >= 100
    ]

def is_recently_active(updated_at: str, months: int = 6) -> bool:
    """Check if account/repo was updated in last N months."""
    try:
        updated = datetime.strptime(updated_at.replace('Z', '+00:00').replace('+00:00', ''), '%Y-%m-%dT%H:%M:%S')
        cutoff = datetime.now() - timedelta(days=months*30)
        return updated > cutoff
    except:
        return False

def fetch_user_repos(username: str) -> List[Dict]:
    """Fetch all public repositories for a user."""
    repos = []
    page = 1

    while True:
        url = f'https://api.github.com/users/{username}/repos'
        params = {
            'per_page': 100,
            'page': page,
            'sort': 'updated',
            'type': 'owner'
        }

        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=10)

            if response.status_code == 403:  # Rate limit
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                wait_time = max(reset_time - time.time(), 0) + 1
                print(f"Rate limited. Waiting {wait_time:.0f} seconds...")
                time.sleep(wait_time)
                continue

            if response.status_code != 200:
                print(f"Error fetching repos for {username}: {response.status_code}")
                break

            data = response.json()
            if not data:
                break

            repos.extend(data)

            if len(data) < 100:
                break

            page += 1
            time.sleep(0.5)  # Be nice to API

        except Exception as e:
            print(f"Exception fetching repos for {username}: {e}")
            break

    return repos

def fetch_recent_commits(owner: str, repo: str) -> Optional[str]:
    """Fetch the date of the most recent commit."""
    url = f'https://api.github.com/repos/{owner}/{repo}/commits'
    params = {'per_page': 1}

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0].get('commit', {}).get('committer', {}).get('date')

    except Exception as e:
        pass

    return None

def calculate_commercial_score(repo: Dict) -> float:
    """
    Calculate commercial potential score (0-10) based on multiple factors.
    """
    score = 0.0

    # Star count (0-3 points)
    stars = repo.get('stargazers_count', 0)
    if stars >= 1000:
        score += 3
    elif stars >= 500:
        score += 2.5
    elif stars >= 100:
        score += 2
    elif stars >= 50:
        score += 1

    # Fork count indicates usefulness (0-1 points)
    forks = repo.get('forks_count', 0)
    if forks >= 100:
        score += 1
    elif forks >= 50:
        score += 0.7
    elif forks >= 20:
        score += 0.5
    elif forks >= 10:
        score += 0.3

    # Has description (0-0.5 points)
    if repo.get('description'):
        score += 0.5

    # Has homepage/documentation (0-0.5 points)
    if repo.get('homepage') or repo.get('has_pages'):
        score += 0.5

    # Open issues indicate active usage (0-1 points)
    issues = repo.get('open_issues_count', 0)
    if 10 <= issues <= 100:
        score += 1
    elif 5 <= issues < 10:
        score += 0.5

    # Language diversity bonus (0-1 points)
    language = repo.get('language', '').lower()
    high_value_langs = ['python', 'javascript', 'typescript', 'go', 'rust', 'java']
    if language in high_value_langs:
        score += 1

    # Topic/keyword matching (0-2 points)
    text_to_check = (
        repo.get('name', '').lower() + ' ' +
        repo.get('description', '').lower() + ' ' +
        ' '.join(repo.get('topics', []))
    )

    monetization_matches = sum(1 for kw in MONETIZATION_KEYWORDS if kw in text_to_check)
    experimental_matches = sum(1 for kw in EXPERIMENTAL_KEYWORDS if kw in text_to_check)

    if monetization_matches >= 3:
        score += 2
    elif monetization_matches >= 2:
        score += 1.5
    elif monetization_matches >= 1:
        score += 1

    # Penalize experimental/learning projects
    if experimental_matches >= 2:
        score -= 2
    elif experimental_matches >= 1:
        score -= 1

    # Not archived (0-1 points)
    if not repo.get('archived', False):
        score += 1
    else:
        score -= 2  # Heavy penalty for archived

    return max(0, min(10, score))

def analyze_monetization_gap(repo: Dict) -> Dict:
    """Analyze if repo has monetization gaps (no pricing, sponsorship, etc)."""
    has_funding = repo.get('has_sponsorships', False)

    # Check for monetization indicators in description/topics
    text = (repo.get('description') or '').lower() + ' ' + ' '.join(repo.get('topics', []))

    has_paid_mention = any(word in text for word in ['paid', 'premium', 'pricing', 'subscription', 'enterprise'])

    return {
        'has_sponsorship': has_funding,
        'has_paid_tier': has_paid_mention,
        'monetization_gap': not (has_funding or has_paid_mention)
    }

def suggest_monetization_strategy(repo: Dict) -> List[str]:
    """Suggest monetization strategies based on repo characteristics."""
    strategies = []

    name = repo.get('name', '').lower()
    desc = (repo.get('description') or '').lower()
    topics = ' '.join(repo.get('topics', []))
    text = f"{name} {desc} {topics}"

    stars = repo.get('stargazers_count', 0)
    language = repo.get('language', '').lower()

    # API/SDK - Freemium with usage tiers
    if any(kw in text for kw in ['api', 'sdk', 'client', 'wrapper']):
        strategies.append("Freemium API service with tiered pricing (free: 1K calls/month, pro: $29/mo unlimited)")
        strategies.append("Enterprise self-hosted license ($5K-50K/year)")

    # Developer tools - Open core model
    if any(kw in text for kw in ['cli', 'tool', 'framework', 'library']):
        strategies.append("Open-core model: Free core + paid enterprise features (SSO, audit logs, support)")
        strategies.append("Managed cloud version ($19-99/month)")

    # AI/ML - Model hosting & API
    if any(kw in text for kw in ['ai', 'ml', 'llm', 'gpt', 'model', 'neural']):
        strategies.append("Hosted API service with per-request pricing ($0.001-0.01 per call)")
        strategies.append("Fine-tuning service for enterprises ($10K+ per project)")
        strategies.append("Consulting & custom model training ($150-300/hour)")

    # Dashboard/Admin - SaaS
    if any(kw in text for kw in ['dashboard', 'admin', 'panel', 'cms']):
        strategies.append("SaaS subscription ($29-299/month per workspace)")
        strategies.append("White-label licensing ($500-5K one-time)")

    # DevOps/Automation - Service + support
    if any(kw in text for kw in ['deploy', 'automation', 'cicd', 'devops']):
        strategies.append("Managed service with infrastructure included ($49-499/month)")
        strategies.append("Enterprise support contract ($2K-10K/year)")

    # Data/Analytics - Data as a service
    if any(kw in text for kw in ['analytics', 'data', 'scraper', 'crawler']):
        strategies.append("Data API with credit-based pricing ($0.001-0.1 per record)")
        strategies.append("Custom data collection services ($5K+ per project)")

    # Security - Consulting heavy
    if any(kw in text for kw in ['security', 'audit', 'vulnerability', 'pentest']):
        strategies.append("Security audit services ($5K-50K per audit)")
        strategies.append("Training & certification programs ($500-2K per person)")

    # General strategies for popular projects
    if stars >= 500:
        strategies.append("GitHub Sponsors + Open Collective ($100-2K/month from community)")
        strategies.append("Course/book about the technology ($29-99 one-time)")

    if stars >= 1000:
        strategies.append("Conference talks & workshop fees ($1K-5K per event)")
        strategies.append("Corporate training ($2K-10K per day)")

    # Fallback strategies
    if not strategies:
        strategies.append("Consulting & implementation services ($100-200/hour)")
        strategies.append("Paid support tiers ($99-999/month)")
        strategies.append("Custom feature development ($5K-50K per feature)")

    return strategies[:3]  # Return top 3 strategies

def estimate_time_to_market(repo: Dict, stars: int) -> str:
    """Estimate time to get first paying customer."""

    if stars >= 1000:
        return "1-2 months (strong existing user base)"
    elif stars >= 500:
        return "2-3 months (good traction, needs positioning)"
    elif stars >= 100:
        return "3-6 months (needs marketing & validation)"
    else:
        return "6-12 months (needs community growth first)"

def estimate_investment(stars: int) -> str:
    """Estimate required investment to monetize."""

    if stars >= 1000:
        return "$5K-15K (hosting, marketing, legal)"
    elif stars >= 500:
        return "$10K-25K (product dev, marketing, infrastructure)"
    elif stars >= 100:
        return "$15K-40K (significant dev work, market validation)"
    else:
        return "$25K-60K (extensive development & marketing needed)"

def analyze_repo_for_monetization(repo: Dict, user: Dict) -> Optional[Dict]:
    """Analyze a single repository for monetization potential."""

    # Basic filters
    stars = repo.get('stargazers_count', 0)
    if stars < 100:
        return None

    if repo.get('archived', False):
        return None

    if repo.get('fork', False):
        return None

    # Check for experimental/low-value project
    text = (repo.get('name', '') + ' ' + (repo.get('description') or '')).lower()
    experimental_matches = sum(1 for kw in EXPERIMENTAL_KEYWORDS if kw in text)
    if experimental_matches >= 2:
        return None

    # Calculate scores
    commercial_score = calculate_commercial_score(repo)
    if commercial_score < 4.0:  # Threshold for consideration
        return None

    # Check recent activity
    pushed_at = repo.get('pushed_at')
    recently_maintained = pushed_at and is_recently_active(pushed_at, months=3)

    # Monetization analysis
    monetization_gap = analyze_monetization_gap(repo)
    if not monetization_gap['monetization_gap']:
        return None  # Already monetized

    strategies = suggest_monetization_strategy(repo)

    return {
        'repo_name': repo.get('name'),
        'repo_url': repo.get('html_url'),
        'description': repo.get('description'),
        'stars': stars,
        'forks': repo.get('forks_count', 0),
        'language': repo.get('language'),
        'topics': repo.get('topics', []),
        'created_at': repo.get('created_at'),
        'updated_at': repo.get('updated_at'),
        'pushed_at': pushed_at,
        'recently_maintained': recently_maintained,
        'open_issues': repo.get('open_issues_count', 0),
        'has_wiki': repo.get('has_wiki', False),
        'has_pages': repo.get('has_pages', False),
        'homepage': repo.get('homepage'),
        'license': repo.get('license', {}).get('name') if repo.get('license') else None,
        'commercial_score': round(commercial_score, 1),
        'monetization_strategies': strategies,
        'time_to_market': estimate_time_to_market(repo, stars),
        'required_investment': estimate_investment(stars),
        'owner': {
            'username': user.get('username'),
            'profile_url': user.get('profile_url'),
            'followers': user.get('followers'),
            'company': user.get('company'),
            'location': user.get('location'),
            'bio': user.get('bio')
        }
    }

def main():
    """Main analysis function."""

    # Load data
    print("Loading stargazers data...")
    stargazers = load_stargazers('/media/terry/data/projects/projects/getidea-git-bank/stargazers_data.json')

    # Filter qualified users
    print("Filtering qualified users (50+ repos, 100+ followers)...")
    qualified_users = filter_qualified_users(stargazers)

    # Further filter for recent activity
    active_users = [
        user for user in qualified_users
        if is_recently_active(user.get('account_updated', ''), months=6)
    ]

    print(f"Found {len(active_users)} active, qualified users")

    # Sort by influence (followers * repos)
    active_users.sort(
        key=lambda u: u.get('followers', 0) * u.get('public_repos_count', 0),
        reverse=True
    )

    # Analyze repositories
    all_opportunities = []
    users_analyzed = 0
    max_users = 30  # Analyze top 30 users (API rate limit consideration)

    for user in active_users[:max_users]:
        username = user.get('username')
        print(f"\n{'='*80}")
        print(f"Analyzing: {username} ({user.get('followers')} followers, {user.get('public_repos_count')} repos)")
        print(f"Company: {user.get('company')} | Location: {user.get('location')}")

        # Fetch repos
        repos = fetch_user_repos(username)
        print(f"Fetched {len(repos)} repositories")

        # Analyze each repo
        user_opportunities = []
        for repo in repos:
            opportunity = analyze_repo_for_monetization(repo, user)
            if opportunity:
                user_opportunities.append(opportunity)

        # Sort by commercial score
        user_opportunities.sort(key=lambda x: x['commercial_score'], reverse=True)

        # Take top 5 per user
        top_opportunities = user_opportunities[:5]

        if top_opportunities:
            print(f"Found {len(top_opportunities)} monetizable repos for {username}")
            for opp in top_opportunities:
                print(f"  - {opp['repo_name']} (★{opp['stars']}, score: {opp['commercial_score']})")

        all_opportunities.extend(top_opportunities)
        users_analyzed += 1

        # Rate limit protection
        time.sleep(2)

    # Sort all opportunities by commercial score
    all_opportunities.sort(key=lambda x: x['commercial_score'], reverse=True)

    # Save results
    output_file = '/media/terry/data/projects/projects/getidea-git-bank/monetization_opportunities.json'
    with open(output_file, 'w') as f:
        json.dump({
            'analysis_date': datetime.now().isoformat(),
            'total_opportunities': len(all_opportunities),
            'users_analyzed': users_analyzed,
            'opportunities': all_opportunities
        }, f, indent=2)

    print(f"\n{'='*80}")
    print(f"Analysis complete!")
    print(f"Total opportunities found: {len(all_opportunities)}")
    print(f"Results saved to: {output_file}")

    # Print summary
    if all_opportunities:
        print(f"\nTop 10 opportunities:")
        for i, opp in enumerate(all_opportunities[:10], 1):
            print(f"{i}. {opp['owner']['username']}/{opp['repo_name']}")
            print(f"   Stars: {opp['stars']} | Score: {opp['commercial_score']} | {opp['time_to_market']}")
            print(f"   Strategy: {opp['monetization_strategies'][0]}")

if __name__ == '__main__':
    main()
