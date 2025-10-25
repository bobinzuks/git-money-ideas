# 🚀 GitHub Actions Setup Guide

## 🎯 What You're Getting

**TWO powerful workflows running for FREE:**

### Workflow 1: Continuous Discovery (Every 12 Hours)
- ⏰ Runs at **2am & 2pm UTC**
- 🔍 **5 discovery scripts in parallel**
- 🧠 **AgentDB training** after each run
- 📊 **Strategic analysis**
- 📧 **Email report** sent automatically
- 💾 **Database persists** (learning accumulates!)

### Workflow 2: Claude Flow Swarm (Every 12 Hours, Offset)
- ⏰ Runs at **8am & 8pm UTC**
- 🐝 **Coordinated multi-agent swarm**
- 🧠 **Neural pattern training**
- 📈 **Performance optimization**
- 📧 **Swarm intelligence report**

**TOTAL: 4 discovery runs per day = 28 runs per week = 120+ runs per month!**

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Add GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** for each of these:

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `GH_TOKEN` | Your GitHub Personal Access Token | [Create here](https://github.com/settings/tokens) (select `public_repo` scope) |
| `EMAIL_FROM` | Your email address | Example: `yourname@gmail.com` |
| `EMAIL_TO` | Where to send reports | Same as EMAIL_FROM or different |
| `EMAIL_PASSWORD` | App-specific password | [Gmail App Passwords](https://myaccount.google.com/apppasswords) |
| `SMTP_SERVER` | (Optional) SMTP server | Default: `smtp.gmail.com` |
| `SMTP_PORT` | (Optional) SMTP port | Default: `587` |

#### 🔑 Getting a GitHub Token:
1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Classic"**
3. Name: `git-money-ideas-discovery`
4. Select scopes: `public_repo`
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)

#### 📧 Getting Gmail App Password:
1. Go to https://myaccount.google.com/apppasswords
2. Name: `GitHub Actions`
3. Click **"Create"**
4. **Copy the 16-character password**

---

### Step 2: Enable Workflows

The workflow files are already created! Just push them:

```bash
git add .github/workflows/
git commit -m "✨ Add automated discovery workflows"
git push
```

---

### Step 3: Manual Test Run (Optional)

Test before waiting 12 hours:

1. Go to **Actions** tab on GitHub
2. Click **"Continuous Discovery & Training"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait ~10-15 minutes
5. Check your email! 📧

---

## 📊 What Happens Automatically

### Every 12 Hours (Main Workflow):

```
2:00 AM/PM UTC:
├─ 🔍 5 Discovery Scripts Run in Parallel (5-10 min)
├─ 🧠 AgentDB Training (2-3 min)
├─ 📊 Strategic Analysis (1-2 min)
├─ 📧 Email Report Generated & Sent (1 min)
└─ 💾 Database Committed to Repo (1 min)

Total Time: ~10-15 minutes
```

### Every 12 Hours (Swarm Workflow, Offset by 6 hours):

```
8:00 AM/PM UTC:
├─ 🐝 Initialize Swarm Coordination (1 min)
├─ 🤖 5 Agents Execute Discovery (5-10 min)
├─ 🧠 Neural Pattern Training (2-3 min)
├─ 📧 Swarm Intelligence Report (1 min)
└─ 💾 Learning Data Persisted (1 min)

Total Time: ~10-15 minutes
```

---

## 📧 Email Report Preview

You'll receive emails like this every 12 hours:

```
Subject: 📊 AgentDB Discovery: 114 Perfect Gems | $22.8K MRR

🎯 Executive Summary:
- New Gems: 24 discovered in last 12 hours
- Quality Trend: IMPROVING 📈 (+15%)
- Revenue Potential: $22,800 MRR
- Algorithm Learning: 3 new patterns detected

💎 Top 3 Discoveries:
1. awesome-mcp-servers (45⭐, 25x multiplier)
   Pain: MCP needs fast memory
   Solution: AgentDB 2-3ms latency
   Action: Email maintainer with demo

[... rest of report ...]

🎯 Top 3 Actions This Week:
1. ✅ Email awesome-mcp-servers maintainer
2. ⏳ Build integration demo
3. ⏳ Create benchmark video
```

---

## 💾 Database Persistence

**Your learning data is automatically saved!**

After each run:
- `continuous_discovery.db` - All discovered repos
- `algorithm_learning_history.json` - Learning patterns
- `*.json` files - Discovery results

These are committed back to your repo, so learning accumulates over time!

---

## 📈 Monitoring Your Workflows

### View Workflow Status:

1. Go to **Actions** tab
2. See all workflow runs
3. Click any run to see details
4. Download artifacts (raw data)

### Check Usage:

1. **Settings** → **Billing and plans**
2. See minutes used (should be 0 - public repos are FREE!)

### Workflow Logs:

Each workflow has detailed logs:
- Discovery progress
- Training metrics
- Email sending status
- Database updates

---

## 🔧 Customization

### Change Schedule:

Edit `.github/workflows/continuous-discovery.yml`:

```yaml
on:
  schedule:
    # Change these cron times
    - cron: '0 2,14 * * *'  # Currently 2am and 2pm UTC
```

**Cron Helper:**
- `0 */6 * * *` - Every 6 hours
- `0 0,12 * * *` - Midnight and noon
- `0 9,21 * * *` - 9am and 9pm

### Run More Frequently:

Want to run every 6 hours? Change both workflows:

```yaml
# Main workflow
- cron: '0 0,6,12,18 * * *'  # Every 6 hours

# Swarm workflow
- cron: '0 3,9,15,21 * * *'  # Offset by 3 hours
```

**Result:** 8 discovery runs per day!

### Disable Email Reports:

Comment out the email step in both workflows:

```yaml
# - name: 📧 Generate Email Report
#   env:
#     EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
#   ...
```

---

## 🐛 Troubleshooting

### ❌ Workflow Fails

**Check:**
1. All secrets are added correctly
2. GitHub token has `public_repo` scope
3. Email password is an **app password**, not regular password
4. SMTP settings are correct for your email provider

### ❌ No Email Received

**Check:**
1. Spam folder
2. Workflow logs: **Actions** → Click run → **report** job
3. Email secrets are correct
4. `automated_report_generator.py` has email code

**Gmail Users:**
- Use App Passwords: https://myaccount.google.com/apppasswords
- Don't use 2FA password

**Outlook/Yahoo:**
- Outlook: `smtp.office365.com:587`
- Yahoo: `smtp.mail.yahoo.com:587`

### ❌ Database Not Persisting

**Check:**
1. `.gitignore` allows `*.db` and `*.json` files
2. Workflow has push permissions
3. Look for commit from `github-actions[bot]`

---

## 💰 Cost Analysis

### For Public Repos (Like Yours):
- ✅ **UNLIMITED** GitHub Actions minutes
- ✅ **FREE** artifact storage (500MB)
- ✅ **FREE** workflow runs

### If You Make Repo Private:
- ✅ Still **2,000 free minutes/month**
- ✅ Each run: ~15 minutes
- ✅ ~130 free runs per month
- ✅ Still covers 4 runs/day!

**You're completely covered! 🎉**

---

## 🎯 What Happens After Setup

1. **Push workflows** → They're active
2. **Wait for scheduled run** OR **trigger manually**
3. **Receive first email** in ~15 minutes
4. **Check database commits** - Learning is persisting
5. **Get reports every 12 hours** automatically

---

## 📊 Expected Results

### Week 1:
- 28 discovery runs (4/day × 7 days)
- ~500-1,000 new repos discovered
- Algorithm learns patterns
- Email reports show trends

### Week 2-4:
- 112 runs total
- 2,000-5,000 repos in database
- Algorithm quality improves 20-30%
- Clear revenue opportunities emerge

### Month 3:
- ~360 runs
- 10,000+ repos analyzed
- Algorithm is finely tuned
- Multiple revenue streams identified

---

## 🚀 Advanced: Run Even More!

Want to maximize free tier usage? You can add MORE workflows:

### Strategy 1: Hourly Discovery
```yaml
# .github/workflows/hourly-discovery.yml
on:
  schedule:
    - cron: '0 * * * *'  # Every hour!
```

### Strategy 2: Different Scripts
```yaml
# Run specific high-value scripts more frequently
on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
```

### Strategy 3: Weekend Bonus
```yaml
# Extra runs on weekends
on:
  schedule:
    - cron: '0 */6 * * 6,0'  # Every 6 hours on Sat/Sun
```

**Public repos = Unlimited minutes = Run as much as you want!**

---

## 📞 Need Help?

1. **Check workflow logs** in Actions tab
2. **Look for commit from bot** - Database should update
3. **Test email manually**: `python automated_report_generator.py`
4. **Check secrets** are all added correctly

---

## 🎉 You're All Set!

Your repository now has:
- ✅ Automated discovery every 12 hours
- ✅ Continuous algorithm training
- ✅ Email reports delivered automatically
- ✅ Database persistence (learning accumulates)
- ✅ Claude Flow swarm intelligence
- ✅ All running FREE on GitHub Actions

**Next email arrives in max 12 hours!** 📧

---

**Built with [Claude Code](https://claude.com/claude-code) 🤖**
