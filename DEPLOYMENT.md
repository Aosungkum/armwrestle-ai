# 🚀 Free Deployment Guide

Complete guide to deploy ArmWrestle AI using **100% free tools**.

---

## 📦 What You'll Deploy

- **Frontend**: Static HTML/CSS/JS
- **Backend**: FastAPI Python server
- **Database**: SQLite (file-based, free)
- **Storage**: Local filesystem

---

## 🎯 Free Hosting Options

### Option 1: Railway (Recommended - Easiest)

**Why Railway?**
- ✅ Free $5/month credit (500 hours)
- ✅ Automatic deployments from GitHub
- ✅ Built-in database support
- ✅ Easy environment management

**Steps:**

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Push Code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/armwrestle-ai.git
   git push -u origin main
   ```

3. **Deploy Backend on Railway**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python
   - Add start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
   - Click "Deploy"

4. **Deploy Frontend**
   - Option A: Same Railway project (add frontend service)
   - Option B: Use Netlify/Vercel (see below)

5. **Get Your Backend URL**
   - Railway provides: `https://your-app.railway.app`
   - Update frontend `auth.js`: Change API_URL to your Railway URL

---

### Option 2: Render.com (Good Alternative)

**Why Render?**
- ✅ Free tier with 750 hours/month
- ✅ Automatic SSL
- ✅ Easy database setup

**Steps:**

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Deploy Backend**
   - "New +" → "Web Service"
   - Connect GitHub repo
   - Settings:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
   - Click "Create Web Service"

3. **Get Backend URL**
   - Render provides: `https://your-app.onrender.com`

**Note**: Render free tier spins down after 15 min of inactivity (cold starts)

---

### Option 3: Fly.io (Most Powerful)

**Why Fly.io?**
- ✅ Free allowance (3 VMs)
- ✅ Global CDN
- ✅ Always-on (no cold starts)

**Steps:**

1. **Install Fly CLI**
   ```bash
   # Mac
   brew install flyctl
   
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login & Deploy**
   ```bash
   flyctl auth signup
   cd backend
   flyctl launch
   # Follow prompts
   flyctl deploy
   ```

3. **Get URL**
   - Fly provides: `https://your-app.fly.dev`

---

## 🎨 Frontend Deployment (All Free)

### Option 1: Netlify (Easiest)

1. **Go to [netlify.com](https://netlify.com)**
2. Drag & drop your `frontend/` folder
3. Done! You get: `https://your-site.netlify.app`

**Or use CLI:**
```bash
npm install -g netlify-cli
cd frontend
netlify deploy --prod
```

### Option 2: Vercel

1. **Go to [vercel.com](https://vercel.com)**
2. Import GitHub repo
3. Root directory: `frontend/`
4. Deploy

### Option 3: GitHub Pages

1. **Enable in repo settings**
2. Push frontend to `gh-pages` branch:
   ```bash
   git subtree push --prefix frontend origin gh-pages
   ```
3. Site available at: `https://yourusername.github.io/armwrestle-ai/`

### Option 4: Cloudflare Pages

1. **Go to [pages.cloudflare.com](https://pages.cloudflare.com)**
2. Connect GitHub
3. Build settings:
   - Build command: (none)
   - Build output: `frontend/`

---

## 🔧 Configuration After Deployment

### 1. Update API URL in Frontend

**In `auth.js`:**
```javascript
// Change this:
this.API_URL = 'http://localhost:8000/api';

// To your deployed backend:
this.API_URL = 'https://your-backend.railway.app/api';
```

**In `script.js`:**
```javascript
// Update the fetch URL:
const response = await fetch('https://your-backend.railway.app/api/analyze', {
    method: 'POST',
    body: formData
});
```

### 2. Enable CORS

Already configured in `api.py`, but verify:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: ["https://your-frontend.netlify.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Environment Variables

**On Railway/Render/Fly:**
- `DATABASE_URL`: (auto-set if using Railway DB)
- `PORT`: (auto-set)

No other env vars needed for MVP!

---

## 📊 Database Setup

### SQLite (Default - No Setup Needed!)

The `armwrestle.db` file is created automatically.

**Important**: On Railway/Render, use persistent volumes:

**Railway:**
- Add volume in settings
- Mount path: `/app/data`
- Update `database.py`: `Database(db_path="/app/data/armwrestle.db")`

**Render:**
- Add disk in settings
- Mount path: `/data`
- Update path accordingly

### Upgrade to PostgreSQL (Still Free!)

**Railway PostgreSQL:**
1. Add PostgreSQL plugin
2. Install `psycopg2`: Add to `requirements.txt`
3. Update `database.py` to use PostgreSQL

**Supabase (Free PostgreSQL):**
1. Sign up at [supabase.com](https://supabase.com)
2. Create project
3. Get connection string
4. Update database connection

---

## 🧪 Testing Deployment

### 1. Test Backend
```bash
curl https://your-backend.railway.app/api/health
```

Expected: `{"status": "healthy"}`

### 2. Test Frontend
- Open: `https://your-site.netlify.app`
- Upload a test video
- Check browser console for errors

### 3. Test Full Flow
1. Register account
2. Upload video
3. View results
4. Check history

---

## 💰 Cost Breakdown (Free Tier Limits)

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Railway** | $5/month credit | ~500 hours |
| **Render** | 750 hours/month | Cold starts after 15 min |
| **Fly.io** | 3 VMs | Always-on |
| **Netlify** | 100GB bandwidth | Unlimited sites |
| **Vercel** | 100GB bandwidth | Unlimited sites |
| **Cloudflare Pages** | Unlimited | 500 builds/month |

**Recommendation**: Railway (backend) + Netlify (frontend) = Best free combo!

---

## 🔒 Security Checklist

- [x] CORS configured correctly
- [ ] Add rate limiting (use `slowapi` package)
- [ ] Add proper authentication (JWT tokens)
- [ ] Validate file uploads (size, type)
- [ ] Add HTTPS (automatic on all platforms)
- [ ] Sanitize user inputs
- [ ] Add API key for production

---

## 🚨 Troubleshooting

### "502 Bad Gateway"
- Backend crashed - check logs
- Increase memory limit in platform settings

### "CORS Error"
- Update `allow_origins` in `api.py`
- Verify frontend URL is correct

### "Database locked"
- SQLite issue with concurrent writes
- Consider upgrading to PostgreSQL

### "Cold Start Slow"
- Normal on Render free tier
- Keep backend warm with cron job:
  ```bash
  # Use cron-job.org to ping every 14 minutes
  curl https://your-backend.onrender.com/api/health
  ```

### Upload Fails
- Check file size limits
- Verify `client_max_body_size` in nginx config
- Increase timeout settings

---

## 📈 Monitoring (Free Tools)

### UptimeRobot
- Monitor uptime
- Get alerts
- Free: 50 monitors

### Better Stack (formerly Logtail)
- Log aggregation
- Error tracking
- Free tier available

### Sentry
- Error tracking
- Performance monitoring
- Free: 5K events/month

---

## 🔄 Auto-Deploy Setup

### Railway
- Automatic on every push to `main`
- No configuration needed

### Render
- Automatic on every push
- Configure branch in settings

### Fly.io
- Manual: `flyctl deploy`
- Auto: Set up GitHub Actions

**GitHub Actions (`.github/workflows/deploy.yml`):**
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: superfly/flyctl-actions@1.3
        with:
          args: "deploy"
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

---

## 🎉 You're Live!

Your ArmWrestle AI is now deployed for **$0/month**!

**Next Steps:**
1. Share your site with users
2. Monitor usage and errors
3. Collect feedback
4. Add payment integration when ready
5. Upgrade to paid tiers as you scale

**Need help?** Check logs:
- Railway: View in dashboard
- Render: Logs tab
- Fly: `flyctl logs`

---

## 💡 Pro Tips

1. **Use CDN**: Cloudflare free tier for static assets
2. **Compress videos**: Add video compression to reduce bandwidth
3. **Cache results**: Add Redis (free tier on Upstash)
4. **Email notifications**: Use Resend free tier
5. **Analytics**: Plausible or Google Analytics

**Happy Deploying! 🚀**