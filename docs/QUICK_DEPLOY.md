# ⚡ 3-Minute GitHub Actions Deploy

## 🚀 Super Quick Setup

### 1️⃣ Add Secrets (2 minutes)

Go to: **Settings** → **Secrets and variables** → **Actions**

Add these 4 secrets:

```
GH_TOKEN       = ghp_xxxxxxxxxxxx (get from: https://github.com/settings/tokens)
EMAIL_FROM     = yourname@gmail.com
EMAIL_TO       = yourname@gmail.com
EMAIL_PASSWORD = xxxx xxxx xxxx xxxx (get from: https://myaccount.google.com/apppasswords)
```

### 2️⃣ Push Workflows (30 seconds)

```bash
git add .github/workflows/
git commit -m "✨ Add automated discovery"
git push
```

### 3️⃣ Test Run (30 seconds)

1. Go to **Actions** tab
2. Click **"Continuous Discovery & Training"**
3. Click **"Run workflow"** → **"Run workflow"**

### ✅ Done!

- Check email in ~15 minutes
- Reports arrive every 12 hours automatically
- Database learns and improves over time

---

## 📊 What You Get

### Main Workflow (2am & 2pm UTC):
- 🔍 5 discovery scripts in parallel
- 🧠 AgentDB training
- 📧 Email report
- 💾 Database persisted

### Swarm Workflow (8am & 8pm UTC):
- 🐝 Coordinated agent swarm
- 🧠 Neural learning
- 📧 Swarm report

**Total: 4 runs per day = FREE on public repos!**

---

## 🔧 Customize Schedule

Edit `.github/workflows/continuous-discovery.yml`:

```yaml
schedule:
  - cron: '0 2,14 * * *'  # Change times here
```

**Popular options:**
- `'0 */6 * * *'` - Every 6 hours (4x/day)
- `'0 */4 * * *'` - Every 4 hours (6x/day)
- `'0 * * * *'` - Every hour (24x/day) - MAX!

**Public repos = UNLIMITED minutes!** 🎉

---

## 📧 Email Report Preview

```
Subject: 📊 Discovery Report: 114 Gems | $22.8K MRR

💎 Top Discoveries:
1. awesome-mcp (45⭐) - $5K MRR potential
2. memory-llm (28⭐) - $8K MRR potential
3. agentdb-tools (19⭐) - $3K MRR potential

🎯 Actions:
- Email 3 maintainers with integration offers
- Build 2 demos this week
- Create benchmark video

[Full details in email...]
```

---

## 🐛 Troubleshooting

### No email?
1. Check spam folder
2. Verify secrets are correct
3. Use Gmail app password (not regular password)

### Workflow failed?
1. Check Actions tab for error logs
2. Verify GitHub token has `public_repo` scope
3. Make sure all 4 secrets are added

### Database not updating?
1. Check for commits from `github-actions[bot]`
2. Verify `.gitignore` allows `.db` files
3. Look in workflow artifacts

---

## 📖 Full Documentation

- **[Complete Setup Guide](GITHUB_ACTIONS_SETUP.md)** - Detailed instructions
- **[Customization](GITHUB_ACTIONS_SETUP.md#customization)** - Change schedules, add features
- **[Troubleshooting](GITHUB_ACTIONS_SETUP.md#troubleshooting)** - Common issues

---

**You're all set! First report arrives in 12 hours (or run manually now)** 🎉
