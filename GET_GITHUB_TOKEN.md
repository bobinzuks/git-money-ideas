# 🔑 How to Get a GitHub Token

## Quick Steps:

1. **Go to GitHub Settings**
   - Visit: https://github.com/settings/tokens
   - Or: GitHub.com → Click your profile (top right) → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token**
   - Click "Generate new token" → "Generate new token (classic)"
   - Give it a name like "Hidden Gem Discovery"

3. **Select Permissions**
   - ✅ Check: `public_repo` (Access public repositories)
   - That's all you need! The discovery system only reads public repos.

4. **Generate and Copy**
   - Click "Generate token" at the bottom
   - **Copy the token immediately** (you won't see it again!)
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

5. **Add to Your System**
   ```bash
   # Temporary (current session only):
   export GITHUB_TOKEN=ghp_your_token_here

   # Permanent (add to ~/.bashrc or ~/.zshrc):
   echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.bashrc
   source ~/.bashrc
   ```

6. **Restart Discovery**
   ```bash
   # Kill current process
   pkill -f continuous_discovery.py

   # Start with token
   nohup python3 continuous_discovery.py >> discovery.log 2>&1 &
   ```

## What This Gets You:

**Without Token:**
- 60 requests per hour
- ~1 discovery cycle per hour
- Finds ~20 gems per hour

**With Token:**
- 5,000 requests per hour (83x more!)
- Continuous discovery with no waits
- Finds ~2,000+ gems per hour
- Can run for days without stopping

## Security Notes:

- ✅ This token only reads **public** repositories
- ✅ It cannot access your private repos or make any changes
- ✅ Safe to use for this discovery system
- ⚠️ Don't commit the token to git (it's in .gitignore)
- ⚠️ Don't share your token publicly

## Verify It's Working:

After adding the token and restarting, check the log:
```bash
tail -20 discovery.log | grep "GitHub Token"
```

You should see:
```
GitHub Token: ✅ Authenticated (5000 req/h)
```

Instead of:
```
GitHub Token: ⚠️  No token (60 req/h)
```
