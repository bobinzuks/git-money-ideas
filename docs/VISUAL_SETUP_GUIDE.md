# 🎯 Visual Step-by-Step Setup Guide

Follow this guide with screenshots to set up your 24/7 automated discovery system!

---

## ✅ Step 1: Workflows Are Already Pushed!

Your workflows are live at:
**https://github.com/bobinzuks/git-money-ideas/actions**

You'll see:
- ✅ **Continuous Discovery & Training** workflow
- ✅ **Claude Flow Swarm Discovery** workflow

Both show "This workflow has a workflow_dispatch event trigger" - that's perfect!

---

## 🔐 Step 2: Add GitHub Secrets (Critical!)

### 2A: Navigate to Secrets Page

**Click this link:**
👉 https://github.com/bobinzuks/git-money-ideas/settings/secrets/actions

Or manually:
1. Go to your repository
2. Click **Settings** (top navigation)
3. Click **Secrets and variables** (left sidebar)
4. Click **Actions**
5. You'll see "Actions secrets and variables"

---

### 2B: Add Secret #1 - GitHub Token

**Get Your Token First:**
1. Open in new tab: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Tokens (classic)"**
3. Name: `git-money-ideas-discovery`
4. Expiration: **No expiration** (or 1 year)
5. Select scopes: ☑️ **`public_repo`** (only this one needed!)
6. Scroll down, click **"Generate token"**
7. **COPY THE TOKEN** (starts with `ghp_`) - you won't see it again!

**Now Add to GitHub:**
1. Go back to secrets page
2. Click **"New repository secret"**
3. Name: `GH_TOKEN`
4. Secret: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx` (paste your token)
5. Click **"Add secret"**

✅ You'll see: "Secret GH_TOKEN was added"

---

### 2C: Add Secret #2 - Email From

1. Click **"New repository secret"**
2. Name: `EMAIL_FROM`
3. Secret: `bobinzuks@gmail.com` (your email)
4. Click **"Add secret"**

✅ Easy!

---

### 2D: Add Secret #3 - Email To

1. Click **"New repository secret"**
2. Name: `EMAIL_TO`
3. Secret: `bobinzuks@gmail.com` (same or different email)
4. Click **"Add secret"**

✅ Done!

---

### 2E: Add Secret #4 - Gmail App Password (Most Important!)

**Get App Password First:**
1. Open in new tab: https://myaccount.google.com/apppasswords
2. Sign in to your Google account
3. If you don't have 2FA enabled, you'll need to enable it first
4. App name: `GitHub Actions` (or any name you want)
5. Click **"Create"**
6. You'll see a **16-character password** like: `abcd efgh ijkl mnop`
7. **COPY THIS PASSWORD**

**Now Add to GitHub:**
1. Go back to secrets page
2. Click **"New repository secret"**
3. Name: `EMAIL_PASSWORD`
4. Secret: `abcdefghijklmnop` (paste without spaces, or with spaces - both work)
5. Click **"Add secret"**

✅ Critical secret added!

---

### 2F: Verify All 4 Secrets

You should now see:
```
Actions secrets (4)
├─ EMAIL_FROM       ✅
├─ EMAIL_PASSWORD   ✅
├─ EMAIL_TO         ✅
└─ GH_TOKEN         ✅
```

**Perfect! Secrets are configured!** 🎉

---

## 🧪 Step 3: Trigger Test Run

### 3A: Go to Actions Page

**Click this link:**
👉 https://github.com/bobinzuks/git-money-ideas/actions

You'll see:
- "All workflows" (left sidebar)
- Your two workflows listed

---

### 3B: Run the Workflow

1. Click **"Continuous Discovery & Training"** (left sidebar)
2. You'll see: "This workflow has a workflow_dispatch event trigger"
3. Look for **"Run workflow"** button (top right, gray button)
4. Click **"Run workflow"**
5. A dropdown appears: Branch: main ✓
6. Click the green **"Run workflow"** button

✅ Workflow is queued!

---

### 3C: Watch It Run

**What you'll see:**

```
Continuous Discovery & Training

● Run workflow (yellow dot)
  Queued - Less than a minute ago

After ~30 seconds:

● Run workflow (yellow dot, spinning)
  In progress - 1 minute ago

  Jobs:
  ● discover-parallel (1/6)
  ⏳ train-agentdb (pending)
  ⏳ analyze (pending)
  ⏳ report (pending)
  ⏳ persist (pending)
  ⏳ summary (pending)

After ~5 minutes:

✅ discover-parallel (completed)
● train-agentdb (running)
⏳ analyze (pending)
...

After ~10-15 minutes:

✅ All jobs completed!
```

---

### 3D: Check the Results

**Click the workflow run** to see details:

```
Jobs completed (6/6)

✅ discover-parallel        5m 23s
✅ train-agentdb           2m 14s
✅ analyze                 1m 47s
✅ report                  52s
✅ persist                 38s
✅ summary                 12s

Total duration: 12m 31s
```

**Scroll down to see:**
- **Artifacts** (discovery results, training data)
- **Workflow summary**

---

## 📧 Step 4: Check Your Email!

### 4A: When to Check

Email is sent during the **"report"** job, which happens ~7-10 minutes into the workflow.

**Timeline:**
- 0-5 min: Discovery running
- 5-7 min: Training
- 7-10 min: Analysis
- **10 min: Email sent** ← Check your inbox!
- 10-12 min: Database committed

---

### 4B: Email Subject

Look for an email with subject like:
```
📊 AgentDB Discovery: X Perfect Gems | $Y MRR
```

Or:
```
📊 AgentDB Discovery Report - [Date]
```

---

### 4C: Email Contents

You'll see a comprehensive report with:

```
📊 AgentDB Discovery Report
══════════════════════════════════════════

🎯 Executive Summary:
- New Gems: 24 discovered
- Total Database: 1,358 repositories
- Quality Trend: IMPROVING 📈 (+15%)
- Revenue Potential: $23,500 MRR

💎 Top 10 Discoveries:
1. awesome-mcp-servers (45⭐, 25x multiplier)
   Category: Communication
   Pain: MCP servers need fast memory
   Fix: AgentDB 2-3ms retrieval
   Revenue: $5,000 MRR potential
   Action: ✅ Email maintainer with demo

[... 9 more gems ...]

🧠 Self-Learning Insights:
- Algorithm improved 12% this cycle
- Best keyword: "memory" (20x multiplier)
- Quality score: 8.7/10
- 3 new patterns detected

💰 Revenue Projections:
Conservative: $3,500 MRR (10% conversion)
Realistic:    $23,500 MRR (20% conversion)
Optimistic:   $47,000 MRR (30% conversion)

🎯 Top 3 Actions This Week:
1. ✅ Email awesome-mcp-servers maintainer
2. ⏳ Build integration demo
3. ⏳ Create 50x speed benchmark video

══════════════════════════════════════════
Next report arrives in 12 hours!
```

---

### 4D: If No Email?

**Check these:**

1. ✅ **Spam/Junk folder** - Check first!
2. ✅ **Workflow logs:**
   - Go to Actions → Click the run → Click "report" job
   - Scroll to "Generate Email Report" step
   - Look for errors

3. ✅ **Secrets are correct:**
   - `EMAIL_PASSWORD` must be an **App Password**, not your regular Gmail password
   - Go back to: https://myaccount.google.com/apppasswords
   - Generate a new one if needed

4. ✅ **Gmail App Passwords enabled:**
   - Requires 2-Factor Authentication
   - Enable 2FA first if not enabled

---

## 🎉 Step 5: You're Done!

### What Happens Now:

✅ **Manual test completed**
✅ **Workflows are configured**
✅ **Secrets are set**
✅ **Email delivery confirmed**

**From now on:**
- Workflows run **automatically every 12 hours**
- No manual triggering needed
- Email reports arrive **4 times per day:**
  - 2:00 AM UTC (Main workflow)
  - 8:00 AM UTC (Swarm workflow)
  - 2:00 PM UTC (Main workflow)
  - 8:00 PM UTC (Swarm workflow)

---

## 📅 Schedule Reference

### UTC to Your Timezone:

**UTC Times:** 2am, 8am, 2pm, 8pm

**Convert to your timezone:**
- **EST (UTC-5):** 9pm, 3am, 9am, 3pm
- **PST (UTC-8):** 6pm, 12am, 6am, 12pm
- **CET (UTC+1):** 3am, 9am, 3pm, 9pm
- **IST (UTC+5:30):** 7:30am, 1:30pm, 7:30pm, 1:30am

Find yours: https://www.timeanddate.com/worldclock/converter.html

---

## 🎯 Quick Links Reference

| What | Link |
|------|------|
| **Actions Dashboard** | https://github.com/bobinzuks/git-money-ideas/actions |
| **Add Secrets** | https://github.com/bobinzuks/git-money-ideas/settings/secrets/actions |
| **GitHub Tokens** | https://github.com/settings/tokens |
| **Gmail App Passwords** | https://myaccount.google.com/apppasswords |
| **Workflow Files** | https://github.com/bobinzuks/git-money-ideas/tree/main/.github/workflows |

---

## 🐛 Common Issues

### Issue: "Resource not accessible by integration"

**Fix:** Enable workflow write permissions
1. Go to: Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select: ☑️ **"Read and write permissions"**
4. Click "Save"

---

### Issue: Workflow runs but no email

**Fix 1:** Check EMAIL_PASSWORD is App Password
- Must be 16-character App Password from Google
- NOT your regular Gmail password
- NOT your 2FA code

**Fix 2:** Check workflow logs
- Actions → Click run → Click "report" job
- Look for email sending step
- See specific error message

---

### Issue: Token expired

**Fix:** Generate new GitHub token
- Tokens expire after set period
- Generate new one at: https://github.com/settings/tokens
- Update `GH_TOKEN` secret with new value

---

## ✅ Verification Checklist

Before closing this guide, verify:

- [ ] All 4 secrets added (GH_TOKEN, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD)
- [ ] Test workflow triggered manually
- [ ] Workflow completed successfully (all green checkmarks)
- [ ] Email received in inbox
- [ ] Automatic schedule is active (next run in Actions tab)

**All checked? You're 100% ready! 🎉**

---

## 🚀 Next Steps

1. **Wait for next scheduled run** (max 12 hours)
2. **Check your email** - reports arrive automatically
3. **Monitor progress** in Actions tab
4. **Watch your database grow** - commits from `github-actions[bot]`

**Your 24/7 automated discovery system is now LIVE!** 🤖

---

*Questions? Check workflow logs in Actions tab for detailed error messages.*
