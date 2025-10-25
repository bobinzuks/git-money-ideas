#!/usr/bin/env python3
"""
Strategic analysis of stargazers based on profile data and known patterns.
"""

import json
from datetime import datetime, timedelta

def load_data():
    with open('/media/terry/data/projects/projects/getidea-git-bank/stargazers_data.json', 'r') as f:
        return json.load(f)

def is_recent(date_str, months=6):
    try:
        date = datetime.strptime(date_str.replace('Z', ''), '%Y-%m-%dT%H:%M:%S')
        return date > datetime.now() - timedelta(days=months*30)
    except:
        return False

def analyze_profile(user):
    """Analyze user profile for commercial potential."""
    score = 0.0

    # Follower count (influence)
    followers = user.get('followers', 0)
    if followers >= 5000: score += 5
    elif followers >= 1000: score += 4
    elif followers >= 500: score += 3
    elif followers >= 100: score += 2

    # Repo count (activity)
    repos = user.get('public_repos_count', 0)
    if repos >= 200: score += 3
    elif repos >= 100: score += 2.5
    elif repos >= 50: score += 2

    # Recent activity
    if is_recent(user.get('account_updated', ''), 6):
        score += 2

    # Company affiliation (credibility)
    company = (user.get('company') or '').lower()
    tier1_companies = ['google', 'microsoft', 'amazon', 'meta', 'facebook', 'apple', 'netflix', 'uber', 'airbnb']
    tier2_companies = ['alibaba', 'tencent', 'bytedance', 'baidu', 'ant', 'antgroup', 'thoughtworks']

    if any(c in company for c in tier1_companies):
        score += 3
    elif any(c in company for c in tier2_companies):
        score += 2
    elif company and company != 'null':
        score += 1

    # Bio indicates technical focus
    bio = (user.get('bio') or '').lower()
    tech_keywords = ['ai', 'ml', 'developer', 'engineer', 'architect', 'devops', 'nlp', 'blockchain', 'cloud']
    if any(kw in bio for kw in tech_keywords):
        score += 1

    # Has blog/website
    if user.get('blog'):
        score += 1

    # Has Twitter (marketing presence)
    if user.get('twitter_username'):
        score += 0.5

    return score

def predict_repo_potential(user):
    """Predict likely monetizable repos based on user profile."""

    predictions = []

    bio = (user.get('bio') or '').lower()
    company = (user.get('company') or '').lower()
    repos = user.get('public_repos_count', 0)
    followers = user.get('followers', 0)

    # High repo count + good following = likely has popular projects
    if repos >= 100 and followers >= 500:
        predictions.append({
            'category': 'Developer Tools & Frameworks',
            'likelihood': 'Very High',
            'typical_stars': '500-5000+',
            'monetization': 'Open-core model, consulting, managed services',
            'revenue_potential': '$50K-500K/year',
            'time_to_market': '1-3 months'
        })

    # AI/ML focus
    if any(kw in bio for kw in ['ai', 'ml', 'nlp', 'llm', 'gpt']):
        predictions.append({
            'category': 'AI/ML Tools & Models',
            'likelihood': 'High',
            'typical_stars': '100-2000',
            'monetization': 'Hosted API, fine-tuning services, consulting',
            'revenue_potential': '$100K-1M+/year',
            'time_to_market': '2-4 months'
        })

    # DevOps/Infrastructure
    if any(kw in bio for kw in ['devops', 'cloud', 'kubernetes', 'docker']):
        predictions.append({
            'category': 'DevOps & Infrastructure Tools',
            'likelihood': 'High',
            'typical_stars': '200-3000',
            'monetization': 'Managed service, enterprise features, support',
            'revenue_potential': '$75K-600K/year',
            'time_to_market': '2-4 months'
        })

    # Blockchain (if mentioned)
    if 'blockchain' in bio or 'web3' in bio:
        predictions.append({
            'category': 'Blockchain Tools & Infrastructure',
            'likelihood': 'Medium',
            'typical_stars': '100-1500',
            'monetization': 'Node services, API access, consulting',
            'revenue_potential': '$50K-400K/year',
            'time_to_market': '3-6 months'
        })

    # Top tier company engineers often have quality side projects
    if any(c in company for c in ['google', 'microsoft', 'amazon', 'meta', 'bytedance', 'alibaba']):
        if not predictions or predictions[0]['category'] != 'Developer Tools & Frameworks':
            predictions.insert(0, {
                'category': 'High-Quality Developer Tools',
                'likelihood': 'Very High',
                'typical_stars': '500-10000+',
                'monetization': 'Consulting, training, enterprise licensing',
                'revenue_potential': '$100K-1M+/year',
                'time_to_market': '1-3 months'
            })

    # Generic prediction for active users
    if not predictions and repos >= 50 and followers >= 100:
        predictions.append({
            'category': 'Open Source Tools/Libraries',
            'likelihood': 'Medium',
            'typical_stars': '100-1000',
            'monetization': 'Support, consulting, premium features',
            'revenue_potential': '$25K-200K/year',
            'time_to_market': '3-6 months'
        })

    return predictions

def generate_report():
    """Generate comprehensive report on monetization opportunities."""

    users = load_data()

    # Filter qualified
    qualified = [
        u for u in users
        if u.get('public_repos_count', 0) >= 50
        and u.get('followers', 0) >= 100
        and is_recent(u.get('account_updated', ''), 6)
    ]

    # Score each
    for user in qualified:
        user['commercial_score'] = analyze_profile(user)
        user['predictions'] = predict_repo_potential(user)

    # Sort by score
    qualified.sort(key=lambda x: x['commercial_score'], reverse=True)

    # Take top 50
    top_50 = qualified[:50]

    # Generate report
    report = {
        'analysis_date': datetime.now().isoformat(),
        'total_qualified_users': len(qualified),
        'top_opportunities_count': len(top_50),
        'methodology': {
            'criteria': 'Users with 50+ repos, 100+ followers, active in last 6 months',
            'scoring_factors': [
                'Follower count (influence)',
                'Repository count (productivity)',
                'Recent activity',
                'Company affiliation',
                'Technical expertise indicators',
                'Online presence (blog, twitter)'
            ],
            'monetization_focus': 'Projects with validated demand, clear use cases, and monetization gaps'
        },
        'key_findings': {
            'total_reach': sum(u['followers'] for u in top_50),
            'total_repositories': sum(u['public_repos_count'] for u in top_50),
            'average_influence_score': round(sum(u['commercial_score'] for u in top_50) / len(top_50), 2),
            'top_companies': list(set(u.get('company') for u in top_50 if u.get('company')))[:10],
            'top_locations': list(set(u.get('location') for u in top_50 if u.get('location')))[:10]
        },
        'high_potential_users': []
    }

    # Build user profiles
    for rank, user in enumerate(top_50, 1):
        profile = {
            'rank': rank,
            'username': user['username'],
            'profile_url': user['profile_url'],
            'commercial_score': round(user['commercial_score'], 1),
            'stats': {
                'followers': user['followers'],
                'public_repos': user['public_repos_count'],
                'following': user['following']
            },
            'profile': {
                'name': user.get('name'),
                'company': user.get('company'),
                'location': user.get('location'),
                'bio': user.get('bio'),
                'blog': user.get('blog'),
                'twitter': user.get('twitter_username')
            },
            'predicted_opportunities': user['predictions'],
            'next_steps': [
                f"Visit https://github.com/{user['username']}?tab=repositories&sort=stargazers",
                "Identify repos with 100+ stars",
                "Check for commercial traction (issues, PRs, community)",
                "Assess monetization gap",
                "Reach out for partnership/acquisition discussion"
            ],
            'estimated_total_potential': calculate_total_potential(user)
        }

        report['high_potential_users'].append(profile)

    return report

def calculate_total_potential(user):
    """Estimate total revenue potential across user's portfolio."""

    repos = user['public_repos_count']
    followers = user['followers']
    score = user['commercial_score']

    # Estimate number of monetizable repos (rough heuristic)
    if repos >= 200:
        monetizable_count = 5-10
    elif repos >= 100:
        monetizable_count = 3-7
    else:
        monetizable_count = 2-5

    # Base revenue per repo based on followers
    if followers >= 5000:
        per_repo_potential = "$100K-500K"
        total_low = monetizable_count.split('-')[0] if isinstance(monetizable_count, str) else 5
        total = f"${total_low * 100}K-{total_low * 500}K"
    elif followers >= 1000:
        per_repo_potential = "$50K-250K"
        total = "$200K-1M"
    elif followers >= 500:
        per_repo_potential = "$25K-150K"
        total = "$100K-500K"
    else:
        per_repo_potential = "$10K-75K"
        total = "$50K-250K"

    return {
        'estimated_monetizable_repos': monetizable_count,
        'revenue_per_repo': per_repo_potential,
        'total_portfolio_potential': total,
        'confidence': 'High' if score >= 12 else 'Medium' if score >= 9 else 'Moderate'
    }

def main():
    print("Generating strategic monetization analysis...")
    print("="*80)

    report = generate_report()

    # Save full report
    output_file = '/media/terry/data/projects/projects/getidea-git-bank/strategic_monetization_report.json'
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nAnalysis complete!")
    print(f"Analyzed {report['total_qualified_users']} qualified users")
    print(f"Identified {report['top_opportunities_count']} high-potential opportunities")
    print(f"\nTotal reach: {report['key_findings']['total_reach']:,} followers")
    print(f"Total repositories: {report['key_findings']['total_repositories']:,}")
    print(f"\nReport saved to: {output_file}")

    # Print top 20 summary
    print(f"\n{'='*80}")
    print(f"TOP 20 HIGH-POTENTIAL USERS FOR MONETIZATION")
    print(f"{'='*80}\n")

    for user in report['high_potential_users'][:20]:
        print(f"{user['rank']}. {user['username']} (Score: {user['commercial_score']}/15)")
        print(f"   Profile: https://github.com/{user['username']}")
        print(f"   Stats: {user['stats']['followers']} followers | {user['stats']['public_repos']} repos")

        if user['profile']['company']:
            print(f"   Company: {user['profile']['company']}")

        if user['profile']['location']:
            print(f"   Location: {user['profile']['location']}")

        if user['predicted_opportunities']:
            pred = user['predicted_opportunities'][0]
            print(f"   Top Opportunity: {pred['category']}")
            print(f"   Revenue Potential: {pred['revenue_potential']}")
            print(f"   Time to Market: {pred['time_to_market']}")

        print(f"   Portfolio Potential: {user['estimated_total_potential']['total_portfolio_potential']}")
        print()

    # Summary statistics
    print(f"{'='*80}")
    print(f"SUMMARY STATISTICS")
    print(f"{'='*80}\n")

    total_users = len(report['high_potential_users'])
    high_score = sum(1 for u in report['high_potential_users'] if u['commercial_score'] >= 12)
    medium_score = sum(1 for u in report['high_potential_users'] if 9 <= u['commercial_score'] < 12)

    print(f"High Priority (Score 12+): {high_score} users - Contact immediately")
    print(f"Medium Priority (Score 9-11): {medium_score} users - Contact within 2 weeks")
    print(f"Lower Priority (Score <9): {total_users - high_score - medium_score} users - Monitor & contact within 1 month")

    print(f"\nTop Companies Represented:")
    for company in report['key_findings']['top_companies'][:10]:
        if company:
            print(f"  - {company}")

    print(f"\nTop Locations:")
    for location in report['key_findings']['top_locations'][:10]:
        if location:
            print(f"  - {location}")

    print(f"\n{'='*80}")
    print(f"RECOMMENDED ACTION PLAN")
    print(f"{'='*80}\n")

    print("PHASE 1 (Week 1-2): High Priority Outreach")
    print("  - Contact top 10 users with score 12+")
    print("  - Review their top starred repositories")
    print("  - Assess acquisition vs partnership opportunity")
    print("  - Budget: $50K-500K per deal")
    print()

    print("PHASE 2 (Week 3-4): Medium Priority Research")
    print("  - Deep dive into repos of users with score 9-11")
    print("  - Identify specific monetizable projects")
    print("  - Begin relationship building")
    print("  - Budget: $25K-250K per deal")
    print()

    print("PHASE 3 (Month 2-3): Portfolio Building")
    print("  - Acquire/license 5-10 high-potential projects")
    print("  - Begin monetization implementation")
    print("  - Launch pilot paid tiers")
    print("  - Expected: First revenue within 90 days")
    print()

    print("EXPECTED OUTCOMES (6 months):")
    print("  - 10-15 monetizable projects acquired/licensed")
    print("  - 5-8 generating revenue")
    print("  - Total revenue: $50K-500K/year projected")
    print("  - Total investment: $200K-800K")
    print("  - Break-even timeline: 12-24 months")

if __name__ == '__main__':
    main()
