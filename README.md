# 💪 ArmWrestle AI - Complete Setup Guide

An AI-powered arm wrestling analysis platform that detects techniques, assesses injury risks, and provides personalized training recommendations.

---

## 📁 Project Structure

```
armwrestle-ai/
├── backend/
│   ├── api.py              # Updated with DB & Auth
│   ├── database.py         # NEW - SQLite operations
│   ├── requirements.txt    # Updated
│   └── Dockerfile          # NEW
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── auth.js             # NEW - Auth module
├── docker-compose.yml      # NEW
├── nginx.conf              # NEW
├── README.md
└── DEPLOYMENT.md           # NEW - Complete deploy guide
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js (optional, for live server)
- Modern web browser

---

## 🔧 Backend Setup (Python)

### 1. Create Project Directory
```bash
mkdir armwrestle-ai
cd armwrestle-ai
mkdir backend frontend
```

### 2. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run Backend Server
```bash
python api.py
```

Backend will run at: **http://localhost:8000**

Test it: Open http://localhost:8000 in browser - you should see API info

---

## 🎨 Frontend Setup

### 1. Place Files
Put these files in the `frontend/` directory:
- `index.html`
- `styles.css`
- `script.js`

### 2. Run Frontend

**Option A: Using Python**
```bash
cd frontend
python -m http.server 3000
```

**Option B: Using Node.js (if installed)**
```bash
npx http-server frontend -p 3000
```

**Option C: Using VS Code**
- Install "Live Server" extension
- Right-click `index.html` → "Open with Live Server"

Frontend will run at: **http://localhost:3000**

---

## 🔌 Connecting Frontend to Backend

In `script.js`, the API endpoint is already configured:
```javascript
const response = await fetch('http://localhost:8000/api/analyze', {
    method: 'POST',
    body: formData
});
```

Make sure:
1. Backend is running on port 8000
2. Frontend is running on port 3000
3. CORS is enabled (already configured in `api.py`)

---

## 🧪 Testing the Application

### 1. Test with Mock Data (Quick)
The frontend currently uses mock data by default for instant testing.

### 2. Test with Real Analysis
To use real AI analysis:

1. Update `analyzeBtn` click handler in `script.js`:
```javascript
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    videoPreview.classList.add('hidden');
    loadingState.classList.remove('hidden');
    
    // Use real API instead of simulation
    const result = await analyzeVideo(selectedFile);
    
    if (result) {
        loadingState.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        displayAPIResults(result.data);
    }
});
```

2. Upload an arm wrestling video
3. Click "Analyze Video"

---

## 📊 API Endpoints

### `GET /`
Health check and API info

### `GET /api/health`
System health status

### `POST /api/analyze`
Full video analysis with AI
- **Input:** Video file (MP4, MOV, AVI)
- **Output:** Complete analysis results

### `POST /api/analyze-simple`
Quick mock analysis for testing
- **Input:** Any video file
- **Output:** Mock analysis data

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3 (Modern design with animations)
- Vanilla JavaScript (No frameworks needed)

### Backend
- **FastAPI** - Fast Python API framework
- **OpenCV** - Video processing
- **MediaPipe** - Pose estimation
- **NumPy** - Numerical computations

---

## 🎯 Features Implemented

✅ Video upload (drag & drop + click)
✅ Video preview with controls
✅ Loading animation with progress
✅ Technique detection (Top Roll, Hook, Press, King's Move)
✅ Injury risk assessment (Elbow, Wrist, Shoulder)
✅ Strength vs Technique analysis
✅ Personalized training recommendations
✅ Responsive design (mobile-friendly)
✅ Smooth animations and transitions

---

## 🔮 Next Steps (Advanced Features)

### Phase 2: Enhanced AI
- [ ] Frame-by-frame breakdown with annotations
- [ ] Fatigue detection algorithm
- [ ] Move prediction engine
- [ ] Compare with pro athletes

### Phase 3: Social Features
- [ ] User accounts & authentication
- [ ] Match history dashboard
- [ ] Skill rating system (ELO)
- [ ] Shareable video clips

### Phase 4: Monetization
- [ ] Subscription system (Stripe/Razorpay)
- [ ] Coach dashboard
- [ ] Team management features
- [ ] White-label reports

---

## 🐛 Troubleshooting

### CORS Errors
If you see CORS errors in browser console:
- Make sure backend is running on port 8000
- CORS middleware is already configured in `api.py`

### Video Upload Fails
- Check file size (must be < 100MB)
- Verify file format (MP4, MOV, AVI only)
- Check browser console for errors

### Backend Crashes
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (must be 3.8+)
- View error logs in terminal

### MediaPipe Issues
MediaPipe requires:
- 64-bit Python
- Windows: Visual C++ Redistributable
- macOS: No special requirements
- Linux: `apt-get install python3-opencv`

---

## 📝 Configuration

### Change Ports

**Backend (api.py):**
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port here
```

**Frontend (script.js):**
```javascript
const response = await fetch('http://localhost:8000/api/analyze', {
    // Change port in URL
});
```

---

## 🚀 Deployment

### Backend Deployment (Railway/Render/AWS)
```bash
# Install requirements
pip install -r requirements.txt

# Run with production settings
uvicorn api:app --host 0.0.0.0 --port $PORT
```

### Frontend Deployment (Netlify/Vercel)
1. Upload frontend files to hosting
2. Update API endpoint in `script.js` to production URL
3. Deploy

---

## 📄 License
MIT License - Feel free to use for personal or commercial projects

---

## 🤝 Contributing
Pull requests welcome! For major changes, open an issue first.

---

## 📧 Support
For issues or questions, create an issue on GitHub or contact support.

---

## 🎉 You're All Set!

Start the backend, open the frontend, and begin analyzing arm wrestling matches!

**Happy Analyzing! 💪**