# 🛡️ NYSE Fortress — Daily Market Briefing Blog

Auto-publishes a daily market strategy briefing to **GitHub Pages** every weekday at **9:35 AM ET**.  
Uses real market data fetched via the **Anthropic Claude API with web search**.

**Your blog URL will be:** `https://chetan864.github.io/nyse-fortress`

---

## ⚡ Setup Guide (15 minutes)

### Step 1 — Create a GitHub Account
If you don't have one: go to **github.com** → Sign Up (free).

---

### Step 2 — Create a New Repository
1. Click the **+** button top-right → **New repository**
2. Name it exactly: `nyse-fortress`
3. Set to **Public**
4. ✅ Check "Add a README file"
5. Click **Create repository**

---

### Step 3 — Upload These Files
1. In your new repo, click **Add file → Upload files**
2. Upload ALL files from this ZIP maintaining the folder structure:
   ```
   _layouts/default.html
   _layouts/post.html
   _includes/   (if any)
   assets/css/main.css
   .github/workflows/daily-briefing.yml
   _posts/       (empty folder — posts go here automatically)
   _config.yml
   index.html
   Gemfile
   generate_briefing.py
   requirements.txt
   ```
3. Commit the upload

---

### Step 4 — Enable GitHub Pages
1. Go to your repo → **Settings** tab
2. Click **Pages** in the left sidebar
3. Under **Source** → select **Deploy from a branch**
4. Branch: **main** | Folder: **/ (root)**
5. Click **Save**
6. Wait ~2 minutes → your site is live at `https://YOUR-USERNAME.github.io/nyse-fortress`

---

### Step 5 — Get Your Anthropic API Key (for real market data)
1. Go to **console.anthropic.com** → Sign up / Log in
2. Click **API Keys** → **Create Key**
3. Copy the key (starts with `sk-ant-...`)
4. ⚠️ You get **$5 free credits** on signup — enough for ~months of daily briefings

---

### Step 6 — Add the API Key as a GitHub Secret
1. In your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: paste your `sk-ant-...` key
5. Click **Add secret**

---

### Step 7 — Update _config.yml
Edit `_config.yml` and change:
```yaml
url: "https://YOUR-GITHUB-USERNAME.github.io"
baseurl: "/nyse-fortress"
```

---

### Step 8 — Test It Manually
1. Go to your repo → **Actions** tab
2. Click **NYSE Fortress Daily Briefing** workflow
3. Click **Run workflow** → **Run workflow**
4. Watch it run (takes ~60 seconds)
5. Visit your blog URL — the first post should appear!

---

## 🕐 Automatic Schedule
The workflow runs automatically **Monday–Friday at 9:35 AM ET**.  
Each run fetches live data and publishes a new dated post.

To change the schedule, edit `.github/workflows/daily-briefing.yml`:
```yaml
- cron: '35 13 * * 1-5'   # M-F 9:35 AM ET
```

---

## 📁 File Structure
```
nyse-fortress/
├── .github/
│   └── workflows/
│       └── daily-briefing.yml    ← Auto-runs daily
├── _layouts/
│   ├── default.html              ← Main HTML shell
│   └── post.html                 ← Individual post layout
├── _posts/                       ← Generated posts land here
│   └── 2026-03-30-morning-briefing.md
├── assets/
│   └── css/
│       └── main.css              ← All styling
├── _config.yml                   ← Jekyll config
├── index.html                    ← Blog homepage
├── Gemfile                       ← Jekyll dependencies
├── generate_briefing.py          ← The data + post generator
└── requirements.txt              ← Python dependencies
```

---

## 💰 Cost
| Service | Cost |
|---|---|
| GitHub (repo + Actions + Pages) | **FREE** |
| Anthropic API (Claude web search) | ~$0.01–0.05/day |
| Domain (optional) | $10–12/year |

---

## 🔧 Troubleshooting
- **Blog not showing?** Check Settings → Pages is enabled
- **Workflow failing?** Check Actions tab for error logs
- **No API key?** The script uses fallback template data — still works!
- **Wrong URL?** Make sure `baseurl` in `_config.yml` matches your repo name
