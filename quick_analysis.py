#!/usr/bin/env python3
"""
Quick analysis focusing on most promising users with batched API calls.
"""

import json
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict

HEADERS = {'Accept': 'application/vnd.github.v3+json'}

def load_stargazers():
    with open('/media/terry/data/projects/projects/getidea-git-bank/stargazers_data.json', 'r') as f:
        return json.load(f)

def is_recent(date_str, months=6):
    try:
        date = datetime.strptime(date_str.replace('Z', ''), '%Y-%m-%dT%H:%M:%S')
        return date > datetime.now() - timedelta(days=months*30)
    except:
        return False

def get_top_users():
    """Get most promising users to analyze."""
    users = load_stargazers()

    qualified = [
        u for u in users
        if u.get('public_repos_count', 0) >= 50
        and u.get('followers', 0) >= 100
        and is_recent(u.get('account_updated', ''), 6)
    ]

    # Score by influence
    for u in qualified:
        u['influence_score'] = u.get('followers', 0) * (u.get('public_repos_count', 0) ** 0.5)

    qualified.sort(key=lambda x: x['influence_score'], reverse=True)

    return qualified[:20]  # Top 20 most influential

def fetch_repos_batch(username, max_repos=50):
    """Fetch repos with aggressive filtering."""
    url = f'https://api.github.com/users/{username}/repos'
    params = {
        'per_page': 100,
        'sort': 'stargazers',
        'direction': 'desc',
        'type': 'owner'
    }

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)

        if response.status_code == 403:
            return None  # Rate limited

        if response.status_code == 200:
            repos = response.json()
            # Filter immediately
            return [
                r for r in repos
                if r.get('stargazers_count', 0) >= 100
                and not r.get('fork', False)
                and not r.get('archived', False)
            ][:max_repos]

    except Exception as e:
        print(f"Error: {e}")

    return []

def score_repo(repo):
    """Quick commercial score calculation."""
    score = 0.0
    stars = repo.get('stargazers_count', 0)

    # Stars
    if stars >= 5000: score += 4
    elif stars >= 1000: score += 3
    elif stars >= 500: score += 2.5
    elif stars >= 100: score += 2

    # Forks
    forks = repo.get('forks_count', 0)
    if forks >= 500: score += 2
    elif forks >= 100: score += 1.5
    elif forks >= 50: score += 1
    elif forks >= 20: score += 0.5

    # Language
    lang = (repo.get('language') or '').lower()
    if lang in ['python', 'javascript', 'typescript', 'go', 'rust']: score += 1.5

    # Description and docs
    if repo.get('description'): score += 0.5
    if repo.get('homepage') or repo.get('has_pages'): score += 0.5

    # Active issues
    issues = repo.get('open_issues_count', 0)
    if 10 <= issues <= 200: score += 1

    # Keywords
    text = (repo.get('name', '') + ' ' + (repo.get('description') or '')).lower()

    good_kw = ['api', 'saas', 'ai', 'ml', 'llm', 'tool', 'framework', 'platform', 'automation', 'deploy']
    bad_kw = ['tutorial', 'learning', 'example', 'demo', 'test', 'course', 'homework']

    good_matches = sum(1 for kw in good_kw if kw in text)
    bad_matches = sum(1 for kw in bad_kw if kw in text)

    score += min(good_matches * 0.5, 2)
    score -= bad_matches * 1.5

    # Recent activity
    if is_recent(repo.get('pushed_at', ''), 3): score += 1

    return max(0, score)

def get_strategies(repo):
    """Quick strategy suggestions."""
    text = (repo.get('name', '') + ' ' + (repo.get('description') or '')).lower()
    stars = repo.get('stargazers_count', 0)

    strategies = []

    if any(kw in text for kw in ['api', 'sdk', 'client']):
        strategies.append("Freemium API service ($29-299/mo)")

    if any(kw in text for kw in ['ai', 'ml', 'llm', 'gpt']):
        strategies.append("Hosted AI API ($0.001-0.01/call)")
        strategies.append("Enterprise fine-tuning ($10K+)")

    if any(kw in text for kw in ['dashboard', 'admin', 'cms']):
        strategies.append("SaaS subscription ($29-299/mo)")

    if any(kw in text for kw in ['cli', 'tool', 'framework']):
        strategies.append("Open-core + managed version ($19-99/mo)")

    if any(kw in text for kw in ['deploy', 'automation', 'devops']):
        strategies.append("Managed service ($49-499/mo)")

    if stars >= 500:
        strategies.append("Consulting & training ($150-300/hr)")

    if not strategies:
        strategies = ["Consulting services ($100-200/hr)", "Paid support ($99-999/mo)"]

    return strategies[:3]

def analyze_user(user):
    """Analyze one user's repositories."""
    username = user['username']

    print(f"\nAnalyzing: {username} ({user['followers']} followers)")

    repos = fetch_repos_batch(username)

    if repos is None:
        return None  # Rate limited

    opportunities = []

    for repo in repos:
        score = score_repo(repo)

        if score >= 5.0:  # High bar
            opportunities.append({
                'repo_name': repo['name'],
                'repo_url': repo['html_url'],
                'description': repo.get('description', 'No description'),
                'stars': repo['stargazers_count'],
                'forks': repo['forks_count'],
                'language': repo.get('language'),
                'updated': repo.get('pushed_at'),
                'score': round(score, 1),
                'strategies': get_strategies(repo),
                'time_to_market': '1-2 months' if repo['stargazers_count'] >= 1000 else '2-4 months',
                'investment': '$5K-20K' if repo['stargazers_count'] >= 1000 else '$15K-40K',
                'owner': {
                    'username': username,
                    'followers': user['followers'],
                    'company': user.get('company'),
                    'location': user.get('location')
                }
            })

    opportunities.sort(key=lambda x: x['score'], reverse=True)

    print(f"Found {len(opportunities)} high-potential repos")

    return opportunities[:5]  # Top 5 per user

def main():
    print("Starting quick analysis...")

    top_users = get_top_users()
    print(f"Analyzing {len(top_users)} top users")

    all_opportunities = []

    for i, user in enumerate(top_users):
        print(f"\n[{i+1}/{len(top_users)}]", end=' ')

        result = analyze_user(user)

        if result is None:  # Rate limited
            print("Rate limited, stopping")
            break

        if result:
            all_opportunities.extend(result)

        time.sleep(1)  # Rate limit protection

    # Sort by score
    all_opportunities.sort(key=lambda x: (x['score'], x['stars']), reverse=True)

    # Save
    output = {
        'analysis_date': datetime.now().isoformat(),
        'total_opportunities': len(all_opportunities),
        'opportunities': all_opportunities
    }

    with open('/media/terry/data/projects/projects/getidea-git-bank/monetization_opportunities.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n\n{'='*80}")
    print(f"Found {len(all_opportunities)} high-potential opportunities")
    print(f"Results saved to monetization_opportunities.json")

    # Top 10 summary
    print(f"\nTOP 10 FAST MONEY MAKERS:")
    print(f"{'='*80}")

    for i, opp in enumerate(all_opportunities[:10], 1):
        print(f"\n{i}. {opp['owner']['username']}/{opp['repo_name']}")
        print(f"   ★ {opp['stars']:,} stars | Score: {opp['score']}/10")
        print(f"   {opp['description'][:80]}")
        print(f"   Strategy: {opp['strategies'][0]}")
        print(f"   Time to Market: {opp['time_to_market']} | Investment: {opp['investment']}")

if __name__ == '__main__':
    main()
