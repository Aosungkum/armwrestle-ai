# Railway Deployment Setup

## Issue: Frontend Not Found

Railway is currently deploying only the `backend/` directory, so the frontend files aren't accessible.

## Solution: Configure Railway Root Directory

### Option 1: Set Root Directory in Railway Dashboard (Recommended)

1. Go to your Railway project dashboard
2. Click on your service
3. Go to **Settings** tab
4. Find **"Root Directory"** or **"Source"** setting
5. **Leave it empty** or set to `/` (root of repository)
6. **DO NOT** set it to `backend/`
7. Save changes

### Option 2: Update Start Command

If Railway is deploying from root but starting from backend:

1. Go to **Settings** → **Deploy**
2. Update **Start Command** to:
   ```
   cd backend && python -m uvicorn api:app --host 0.0.0.0 --port $PORT
   ```
   (This should already be set in `railway.json`)

### Option 3: Use nixpacks.toml (Alternative)

Create `nixpacks.toml` in repository root:

```toml
[phases.setup]
nixPkgs = ["python3", "pip"]

[phases.install]
cmds = ["pip install -r backend/requirements.txt"]

[start]
cmd = "cd backend && python -m uvicorn api:app --host 0.0.0.0 --port $PORT"
```

## Verify Configuration

After updating Railway settings:

1. **Redeploy** your service
2. Check **Logs** for:
   - `[DEBUG] Contents of /app:` - Should show both `backend/` and `frontend/` directories
   - `[INFO] Found frontend at: /app/frontend` - Should find frontend
3. Visit your Railway URL - Should see the website, not JSON

## Current Status

- ✅ API code checks for frontend at multiple paths
- ✅ Frontend files are in repository root
- ⚠️ Railway needs to be configured to deploy from root (not just backend/)

