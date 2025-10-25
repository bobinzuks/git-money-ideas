#!/usr/bin/env python3
"""
Fetch stargazers from DB-GPT repository
"""
import requests
import json
import time
import sys
from datetime import datetime

# Configuration
REPO_OWNER = "eosphoros-ai"
REPO_NAME = "DB-GPT"
OUTPUT_FILE = "/media/terry/data/projects/projects/getidea-git-bank/stargazers_data.json"
TARGET_COUNT = 1000  # Fetch 1000 stargazers
PER_PAGE = 100

def get_github_token():
    """Try to get GitHub token from gh CLI"""
    try:
        import subprocess
        result = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True, check=False)
        if result.returncode == 0 and result.stdout.strip():
            token = result.stdout.strip()
            print(f"Found GitHub token (length: {len(token)})", file=sys.stderr)
            return token
    except Exception as e:
        print(f"Warning: Could not get GitHub token: {e}", file=sys.stderr)
    return None

def fetch_stargazers_page(page, token=None):
    """Fetch a single page of stargazers"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/stargazers"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    params = {
        "per_page": PER_PAGE,
        "page": page
    }

    print(f"Fetching page {page}...", file=sys.stderr)
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403:
        print(f"Rate limit exceeded. Waiting...", file=sys.stderr)
        time.sleep(60)
        return fetch_stargazers_page(page, token)
    else:
        print(f"Error: {response.status_code} - {response.text}", file=sys.stderr)
        return []

def fetch_user_details(username, token=None):
    """Fetch detailed information for a user"""
    url = f"https://api.github.com/users/{username}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403:
        print(f"Rate limit exceeded. Waiting...", file=sys.stderr)
        time.sleep(60)
        return fetch_user_details(username, token)
    else:
        print(f"Error fetching {username}: {response.status_code}", file=sys.stderr)
        return None

def main():
    token = get_github_token()
    if token:
        print("Using authenticated GitHub token", file=sys.stderr)
    else:
        print("No GitHub token found. Using unauthenticated requests (limited to 60/hour)", file=sys.stderr)

    all_stargazers = []
    page = 1
    pages_needed = (TARGET_COUNT + PER_PAGE - 1) // PER_PAGE

    print(f"Fetching {TARGET_COUNT} stargazers from {REPO_OWNER}/{REPO_NAME}...", file=sys.stderr)

    while len(all_stargazers) < TARGET_COUNT:
        stargazers = fetch_stargazers_page(page, token)

        if not stargazers:
            print(f"No more stargazers found at page {page}", file=sys.stderr)
            break

        print(f"Processing {len(stargazers)} stargazers from page {page}...", file=sys.stderr)

        for idx, stargazer in enumerate(stargazers):
            if len(all_stargazers) >= TARGET_COUNT:
                break

            username = stargazer.get('login')
            print(f"  [{len(all_stargazers) + 1}/{TARGET_COUNT}] Fetching details for {username}...", file=sys.stderr)

            # Fetch detailed user info
            user_details = fetch_user_details(username, token)

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
                    "public_gists": user_details.get('public_gists', 0)
                }
                all_stargazers.append(user_data)

            # Rate limiting - be nice to GitHub API
            time.sleep(0.5)

        page += 1

        # Save intermediate results every page
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
    print(f"Average public repos: {sum(s['public_repos_count'] for s in all_stargazers) / len(all_stargazers):.1f}", file=sys.stderr)
    print(f"Average followers: {sum(s['followers'] for s in all_stargazers) / len(all_stargazers):.1f}", file=sys.stderr)
    print(f"Users with 10+ public repos: {sum(1 for s in all_stargazers if s['public_repos_count'] >= 10)}", file=sys.stderr)
    print(f"Users with 100+ followers: {sum(1 for s in all_stargazers if s['followers'] >= 100)}", file=sys.stderr)

if __name__ == "__main__":
    main()
