# DB-GPT Repository Stargazers Analysis

## Overview
This dataset contains comprehensive information about 1,000 stargazers from the DB-GPT repository (https://github.com/eosphoros-ai/DB-GPT).

**Data Collection Date:** October 24, 2025  
**Total Stargazers in Repo:** 17,505  
**Sample Size:** 1,000 users (first 1,000 stargazers)

## File Information
- **File:** `/media/terry/data/projects/projects/getidea-git-bank/stargazers_data.json`
- **Size:** 520 KB
- **Format:** JSON array with detailed user metadata

## Data Structure
Each stargazer record contains:
- `username`: GitHub username
- `profile_url`: GitHub profile URL
- `public_repos_count`: Number of public repositories
- `followers`: Number of followers
- `following`: Number of users followed
- `account_created`: Account creation date
- `account_updated`: Last account update
- `bio`: User biography
- `location`: Geographic location
- `company`: Company affiliation
- `blog`: Personal website/blog
- `twitter_username`: Twitter handle
- `hireable`: Hiring status
- `public_gists`: Number of public gists
- `avatar_url`: Profile picture URL
- `name`: Full name

## Key Statistics

### Repository Activity
- **Average Public Repos:** 69 repositories per user
- **Maximum Public Repos:** 2,147 repositories
- **Users with 10+ repos:** 680 (68%)
- **Users with 50+ repos:** 291 (29.1%)
- **Users with 100+ repos:** 155 (15.5%)

### Community Engagement
- **Average Followers:** 51 followers per user
- **Maximum Followers:** 5,332 followers
- **Users with 100+ followers:** 84 (8.4%)
- **Users with 500+ followers:** 13 (1.3%)
- **Users with 1000+ followers:** 7 (0.7%)

## Top Users by Repository Count
1. **ai-ml-architect** - 2,147 repos, 134 followers
2. **kouweizhong** - 1,724 repos, 20 followers
3. **mbaneshi** - 1,654 repos, 185 followers
4. **yibit** - 1,593 repos, 77 followers
5. **evdcush** - 1,520 repos, 20 followers

## Top Influencers by Followers
1. **wx-chevalier** - 5,332 followers, 178 repos (UnionTech)
2. **nikivdev** - 4,914 followers, 533 repos
3. **xudafeng** - 2,575 followers, 125 repos (Alibaba ecosystem)
4. **lihengming** - 1,505 followers, 23 repos (Alibaba)
5. **FunnyWolf** - 1,329 followers, 95 repos (Philips)

## Notable Patterns
- Many stargazers are from tech companies (Alibaba, Ant Group, Philips)
- Significant Chinese developer community presence
- Mix of individual developers and enterprise users
- High percentage of active developers (68% with 10+ repos)

## Use Cases for This Data
1. **Market Research:** Understand the DB-GPT user base
2. **Developer Outreach:** Identify potential contributors/collaborators
3. **Competitive Analysis:** See what other projects these users star
4. **Community Building:** Connect with influential community members
5. **Product Development:** Learn from active developers' other projects

## Access Methods

### View summary statistics:
```bash
jq 'length, ([.[].public_repos_count] | add / length | floor), ([.[].followers] | add / length | floor)' stargazers_data.json
```

### Find users with specific criteria:
```bash
# Users with 100+ repos and 100+ followers
jq '[.[] | select(.public_repos_count >= 100 and .followers >= 100)]' stargazers_data.json

# Users from specific company
jq '[.[] | select(.company != null and (.company | contains("Alibaba")))]' stargazers_data.json
```

### Export to CSV:
```bash
jq -r '["username","profile_url","public_repos_count","followers","company","location"], (.[] | [.username, .profile_url, .public_repos_count, .followers, .company, .location]) | @csv' stargazers_data.json > stargazers.csv
```

## Next Steps
You can now:
1. Analyze their repository topics/languages to find monetization patterns
2. Cross-reference with other popular repos they've starred
3. Identify common technologies and tools used
4. Reach out to influential users for collaboration
5. Study successful projects from top contributors
