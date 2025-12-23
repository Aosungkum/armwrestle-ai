# Deploy Frontend to GitHub Pages

## Quick Setup

### Step 1: Enable GitHub Pages

1. Go to your GitHub repository: `https://github.com/Aosungkum/armwrestle-ai`
2. Click **Settings** → **Pages**
3. Under **Source**, select:
   - **Branch**: `main`
   - **Folder**: `/frontend`
4. Click **Save**

### Step 2: Get Your GitHub Pages URL

Your site will be available at:
```
https://aosungkum.github.io/armwrestle-ai/
```

(Replace `aosungkum` with your GitHub username)

### Step 3: Update Frontend API URL

The frontend is already configured to use Railway backend:
- `frontend/auth.js` → Uses `https://armwrestle-ai-production.up.railway.app/api`
- `frontend/script.js` → Uses `https://armwrestle-ai-production.up.railway.app`

**No changes needed!** ✅

### Step 4: Verify CORS

The backend already allows all origins (`allow_origins=["*"]`), so GitHub Pages will work.

## Alternative: Custom Domain

If you have a custom domain:

1. Add `CNAME` file in `frontend/` directory:
   ```
   yourdomain.com
   ```

2. Update DNS records to point to GitHub Pages

3. Update frontend API URLs to use your custom domain (if backend is also on custom domain)

## Testing

1. Push any changes to `main` branch
2. GitHub Pages auto-deploys (takes 1-2 minutes)
3. Visit: `https://aosungkum.github.io/armwrestle-ai/`
4. Test video upload - should connect to Railway backend

## Troubleshooting

### 404 Errors
- Make sure `/frontend` folder is selected in GitHub Pages settings
- Check that files are in `frontend/` directory in repository

### CORS Errors
- Backend already allows all origins
- If issues persist, check Railway backend logs

### API Not Connecting
- Verify Railway backend URL is correct in `frontend/auth.js` and `frontend/script.js`
- Check Railway backend is running and accessible

