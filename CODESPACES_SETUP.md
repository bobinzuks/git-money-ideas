# ☁️ GitHub Codespaces - One-Click Setup

## 🚀 Launch in 60 Seconds

### Step 1: Create Codespace (30 seconds)

1. **Go to:** https://github.com/bobinzuks/git-money-ideas
2. **Click:** Green "Code" button
3. **Select:** "Codespaces" tab
4. **Click:** "Create codespace on main"
5. **Wait:** ~30 seconds for setup

### Step 2: Configure (30 seconds)

**In the Codespace terminal:**

```bash
./setup_email_config.sh
```

**You'll need:**
- Email address (Gmail/Outlook)
- App password ([get one](https://myaccount.google.com/apppasswords))
- GitHub token ([create one](https://github.com/settings/tokens))

### Step 3: Start (10 seconds)

```bash
./start_all.sh
```

**Done!** ✅

---

## 🎯 What Happens Automatically

When you create a Codespace:

1. ✅ **Python 3.11** installed
2. ✅ **Dependencies** installed (`pip install -r requirements.txt`)
3. ✅ **Scripts** made executable
4. ✅ **Port 5000** forwarded (dashboard)
5. ✅ **Git** configured
6. ✅ **GitHub CLI** ready

---

## 📊 After Setup

### Verify Everything Works:

```bash
# Check status
./start_all.sh

# Should show:
# ✅ Discovery engine running
# ✅ Dashboard API running
# ✅ Cron jobs configured
# 📊 Database: X gems discovered
```

### Access Dashboard:

1. Look for **"Ports"** tab in VS Code
2. Find **port 5000** (Discovery Dashboard)
3. Click **globe icon** to open
4. See live gem discoveries!

### Test Email Reports:

```bash
# Generate report now (don't wait 12 hours)
python3 automated_report_generator.py

# Check your email!
```

---

## ⚙️ Codespace Management

### Keep Alive:

Codespaces auto-stop after **30 minutes of inactivity**.

**To keep running 24/7:**

1. **Settings** → **Codespaces**
2. **Timeout:** Set to max (4 hours for Free, 24+ hours for Pro)
3. **Or:** Run in background and resume when needed

**Note:** Discovery continues in database even after stop/resume.

### Resume After Stop:

```bash
# Just run this again
./start_all.sh

# Everything restarts automatically!
```

### View Logs:

```bash
# Discovery engine
tail -f discovery_v2.log

# Reports
tail -f reports.log

# Dashboard
tail -f dashboard.log
```

---

## 💰 Cost

### Free Tier:
- **60 hours/month** free
- **2-core** machine
- Perfect for testing!

### Calculation:
- 24/7 operation = 720 hours/month
- **Free tier**: 60 hours = ~2.5 days
- **After free**: ~$130/month (2-core)

### Recommendation:
1. **Start with free tier** - Test for 2-3 days
2. **Validate value** - Ensure reports are useful
3. **Upgrade if profitable** - Worth it if first customer > $130/month

---

## 🔧 Customization in Codespaces

### Change Report Schedule:

```bash
crontab -e

# Change times:
0 6,18 * * *   # 6 AM & 6 PM
0 */6 * * *    # Every 6 hours
0 9 * * *      # Daily 9 AM only
```

### Change Discovery Parameters:

Edit `continuous_discovery.py`:

```python
# Line 358: Star range
has_real_traction = stars >= 5 and stars <= 100

# Line 362: Multiplier threshold
high_multiplier = score_data['agentdb_multiplier'] >= 15
```

Then restart:
```bash
pkill -f continuous_discovery.py
./start_all.sh
```

### Add More Queries:

Edit `continuous_discovery.py` lines 251-295:

```python
all_queries = [
    ('your custom query', 100),
    ('another search term', 100),
    # ... add more
]
```

---

## 🐛 Troubleshooting

### Codespace Won't Start?

**Check:**
1. Codespace limits (max 10 per account)
2. Organization permissions
3. Try different browser

**Fix:**
- Delete old Codespaces
- Try Incognito mode
- Use GitHub Desktop

### Port 5000 Not Accessible?

**Check:**
1. Port forwarding tab in VS Code
2. Dashboard API running: `pgrep -f flask`

**Fix:**
```bash
# Restart dashboard
pkill -f flask
cd wasm-web
python3 -m flask run --host=0.0.0.0 --port=5000 &
```

### Email Not Sending?

**Check `.env` file:**
```bash
cat .env | grep -E "SMTP|EMAIL"
```

**Test SMTP:**
```bash
python3 -c "
import smtplib, os
from dotenv import load_dotenv
load_dotenv()
s = smtplib.SMTP(os.getenv('SMTP_HOST'), 587)
s.starttls()
s.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
print('✅ Works!')
s.quit()
"
```

### Discovery Not Finding Gems?

**Check logs:**
```bash
tail -100 discovery_v2.log
```

**Common issues:**
- GitHub rate limit hit (wait 1 hour)
- No GITHUB_TOKEN in .env
- Discovery process crashed

**Fix:**
```bash
# Restart discovery
pkill -f continuous_discovery.py
python3 continuous_discovery.py >> discovery_v2.log 2>&1 &
```

---

## 📱 Mobile Access

Yes, you can access Codespaces from mobile!

1. **Install:** GitHub Mobile app
2. **Open:** Repository
3. **Code → Codespaces**
4. **View:** In browser or app

**Note:** Best for monitoring, not editing.

---

## 🔒 Security in Codespaces

### What's Protected:

✅ `.env` file (never committed)
✅ Database files (never committed)
✅ Log files (never committed)
✅ API tokens (in environment only)

### What's Safe:

✅ All Python code
✅ Documentation
✅ Scripts
✅ Database schema

### Best Practices:

1. **Never commit `.env`** (already in .gitignore)
2. **Rotate GitHub token** every 90 days
3. **Use app passwords** (not real passwords)
4. **Delete Codespace** when done (data in GitHub repo is safe)

---

## 💾 Data Persistence

### What Persists:

✅ **Code changes** (commit & push)
✅ **Git commits** (in repo)
✅ **Configuration** (.devcontainer/)

### What Doesn't Persist (After Delete):

❌ Database files (`.db`)
❌ Log files (`.log`)
❌ Environment variables (`.env`)
❌ Running processes

### To Preserve Data:

```bash
# Before deleting Codespace:

# 1. Export database
cp continuous_discovery.db ~/exported_db.db

# 2. Commit changes
git add . && git commit -m "Update" && git push

# 3. Download .env backup
# (File → Download → .env)
```

---

## 🚀 Advanced: Multiple Codespaces

You can run multiple Codespaces for different purposes:

### Codespace 1: Production
- 24/7 discovery
- Email reports
- Main database

### Codespace 2: Testing
- Try new queries
- Test parameter changes
- Separate database

### Codespace 3: Development
- Code changes
- Build new features
- Testing environment

---

## 📊 Monitoring

### Check System Status:

```bash
# Everything at once
./start_all.sh

# Individual components
pgrep -f continuous_discovery  # Discovery engine
pgrep -f flask                 # Dashboard
crontab -l                     # Cron jobs
```

### Database Stats:

```bash
sqlite3 continuous_discovery.db "
  SELECT COUNT(*) as total_gems,
         SUM(CASE WHEN stars >= 5 AND stars <= 100
             AND forks > 0 AND agentdb_multiplier >= 15
             THEN 1 ELSE 0 END) as perfect_gems
  FROM discovered_gems;
"
```

### Real-Time Discovery:

```bash
# Watch new gems appear
tail -f discovery_v2.log | grep "💎 FOUND"
```

---

## ✅ Checklist

After Codespace creation:

- [ ] Run `./setup_email_config.sh`
- [ ] Configure email + GitHub token
- [ ] Run `./start_all.sh`
- [ ] Verify dashboard (port 5000)
- [ ] Test email: `python3 automated_report_generator.py`
- [ ] Check email inbox
- [ ] Verify cron: `crontab -l`
- [ ] Check logs: `tail -f *.log`
- [ ] Star the repo ⭐

---

## 🎉 You're Live!

**What's happening now:**

1. Discovery engine scanning GitHub 24/7
2. Database growing with hidden gems
3. Algorithm learning patterns
4. Reports generating every 12 hours
5. Emails arriving with opportunities

**Your job:**

1. Read reports
2. Take top 3 actions
3. Build integrations
4. Make money

---

## 📚 Next Steps

- **[QUICK_START.md](QUICK_START.md)** - Quick reference
- **[README_AUTOMATION.md](README_AUTOMATION.md)** - Full guide
- **[FASTEST_PATH_TO_10K_REVENUE.md](FASTEST_PATH_TO_10K_REVENUE.md)** - Business strategy

---

**🚀 Happy discovering in the cloud!**
