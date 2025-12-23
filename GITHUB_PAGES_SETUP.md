# GitHub Pages Setup - Step by Step

## ✅ Frontend Files Are in Repository

The `frontend/` folder is already in your GitHub repository with these files:
- `frontend/index.html`
- `frontend/auth.js`
- `frontend/script.js`
- `frontend/styles.css`
- `frontend/dashboard.html`
- `frontend/dashboard.js`

## 🔧 Setup GitHub Pages

### Step 1: Go to Repository Settings

1. Open: `https://github.com/Aosungkum/armwrestle-ai`
2. Click **"Settings"** tab (top menu, far right)
3. Scroll down to **"Pages"** in the left sidebar
4. Click **"Pages"**

### Step 2: Configure Source

Under **"Build and deployment"**:

1. **Source**: Select **"Deploy from a branch"**
2. **Branch**: 
   - Select: `main`
   - Folder: Select **`/ (root)`** first, then change to **`/frontend`**
   
   **IMPORTANT**: If you don't see `/frontend` option:
   - Make sure you selected `main` branch first
   - The folder dropdown should show: `/ (root)`, `/docs`, `/frontend`
   - If `/frontend` doesn't appear, refresh the page

3. Click **"Save"**

### Step 3: Wait for Deployment

- GitHub will show: "Your site is ready to be published"
- After 1-2 minutes, you'll see: "Your site is live at..."
- URL will be: `https://aosungkum.github.io/armwrestle-ai/`

## 🔍 If `/frontend` Folder Doesn't Appear

### Option A: Check Repository Structure

1. Go to: `https://github.com/Aosungkum/armwrestle-ai/tree/main`
2. You should see folders: `backend/`, `frontend/`, etc.
3. Click on `frontend/` folder
4. You should see: `index.html`, `auth.js`, `script.js`, etc.

### Option B: Use Root Folder (Alternative)

If `/frontend` still doesn't appear:

1. In GitHub Pages settings, select **`/ (root)`** folder
2. This will serve from repository root
3. Your site URL will be: `https://aosungkum.github.io/armwrestle-ai/`
4. But you'll need to access files as: `https://aosungkum.github.io/armwrestle-ai/frontend/index.html`

**Better solution**: Move frontend files to root (see below)

## 🎯 Alternative: Move Frontend to Root (Recommended if folder option doesn't work)

If GitHub Pages doesn't show `/frontend` option, we can move files to root:

1. Copy `frontend/index.html` → `index.html` (root)
2. Copy other frontend files to root
3. Update paths in HTML files
4. Deploy from `/ (root)` folder

**Let me know if you want me to do this!**

## ✅ Verify Setup

After enabling GitHub Pages:

1. Visit: `https://aosungkum.github.io/armwrestle-ai/`
2. You should see your ArmWrestle AI homepage
3. Test video upload - should connect to Railway backend

## 🔗 Your URLs

- **Frontend**: `https://aosungkum.github.io/armwrestle-ai/`
- **Backend API**: `https://armwrestle-ai-production.up.railway.app/api`

Frontend is already configured to use Railway backend - no changes needed!

