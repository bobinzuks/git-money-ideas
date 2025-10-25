#!/usr/bin/env python3
"""
Fetch stargazers from DB-GPT repository using gh CLI for authentication
"""
import subprocess
import json
import time
import sys
from datetime import datetime

# Configuration
REPO_OWNER = "eosphoros-ai"
REPO_NAME = "DB-GPT"
REPO = f"{REPO_OWNER}/{REPO_NAME}"
OUTPUT_FILE = "/media/terry/data/projects/projects/getidea-git-bank/stargazers_data.json"
TARGET_COUNT = 1000  # Fetch 1000 stargazers
PER_PAGE = 100

def gh_api_call(endpoint):
    """Make GitHub API call using gh CLI"""
    cmd = ['gh', 'api', endpoint]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error calling {endpoint}: {result.stderr}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Exception calling {endpoint}: {e}", file=sys.stderr)
        return None

def fetch_stargazers_page(page):
    """Fetch a single page of stargazers"""
    endpoint = f"/repos/{REPO}/stargazers?per_page={PER_PAGE}&page={page}"

    print(f"Fetching page {page}...", file=sys.stderr)
    return gh_api_call(endpoint)

def fetch_user_details(username):
    """Fetch detailed information for a user"""
    endpoint = f"/users/{username}"
    return gh_api_call(endpoint)

def main():
    print(f"Using gh CLI for authenticated GitHub API access", file=sys.stderr)

    all_stargazers = []
    page = 1

    print(f"Fetching {TARGET_COUNT} stargazers from {REPO}...", file=sys.stderr)

    while len(all_stargazers) < TARGET_COUNT:
        stargazers = fetch_stargazers_page(page)

        if not stargazers or len(stargazers) == 0:
            print(f"No more stargazers found at page {page}", file=sys.stderr)
            break

        print(f"Processing {len(stargazers)} stargazers from page {page}...", file=sys.stderr)

        for stargazer in stargazers:
            if len(all_stargazers) >= TARGET_COUNT:
                break

            username = stargazer.get('login')
            print(f"  [{len(all_stargazers) + 1}/{TARGET_COUNT}] Fetching details for {username}...", file=sys.stderr)

            # Fetch detailed user info
            user_details = fetch_user_details(username)

            if user_details:
                user_data = {
                    "username": username,
                    "profile_url": user_details.get('html_url'),
                    "public_repos_count": user_details.get('public_repos', 0),
                    "followers": user_details.get('followers', 0),
                    "following": user_details.get('following', 0),
                    "account_created": user_details.get('created_at'),
                    "account_updated": user_details.get('updated_at'),
                    "bio": user_details.get('bio'),
                    "location": user_details.get('location'),
                    "company": user_details.get('company'),
                    "blog": user_details.get('blog'),
                    "twitter_username": user_details.get('twitter_username'),
                    "hireable": user_details.get('hireable'),
                    "public_gists": user_details.get('public_gists', 0),
                    "avatar_url": user_details.get('avatar_url'),
                    "name": user_details.get('name')
                }
                all_stargazers.append(user_data)

            # Small delay to avoid overwhelming the API
            time.sleep(0.3)

        page += 1

        # Save intermediate results every 2 pages
        if page % 2 == 0:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(all_stargazers, f, indent=2)
            print(f"Intermediate save: {len(all_stargazers)} stargazers saved", file=sys.stderr)

    # Final save
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_stargazers, f, indent=2)

    print(f"\n✓ Successfully fetched {len(all_stargazers)} stargazers", file=sys.stderr)
    print(f"✓ Data saved to: {OUTPUT_FILE}", file=sys.stderr)

    # Print summary statistics
    print("\n=== Summary Statistics ===", file=sys.stderr)
    print(f"Total stargazers fetched: {len(all_stargazers)}", file=sys.stderr)
    if all_stargazers:
        print(f"Average public repos: {sum(s['public_repos_count'] for s in all_stargazers) / len(all_stargazers):.1f}", file=sys.stderr)
        print(f"Average followers: {sum(s['followers'] for s in all_stargazers) / len(all_stargazers):.1f}", file=sys.stderr)
        print(f"Users with 10+ public repos: {sum(1 for s in all_stargazers if s['public_repos_count'] >= 10)}", file=sys.stderr)
        print(f"Users with 100+ followers: {sum(1 for s in all_stargazers if s['followers'] >= 100)}", file=sys.stderr)

        # Top users by repo count
        top_by_repos = sorted(all_stargazers, key=lambda x: x['public_repos_count'], reverse=True)[:5]
        print("\nTop 5 users by public repos:", file=sys.stderr)
        for user in top_by_repos:
            print(f"  - {user['username']}: {user['public_repos_count']} repos, {user['followers']} followers", file=sys.stderr)

if __name__ == "__main__":
    main()
