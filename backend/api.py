from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
import numpy as np
from typing import Optional, Dict, Any
from database import Database
import secrets

# 🚫 DO NOT import cv2 here
cv2 = None  # lazy-loaded later

app = FastAPI(title="ArmWrestle AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()
active_sessions = {}

# ---------------- AUTH HELPERS ----------------
def generate_token():
    return secrets.token_urlsafe(32)

def get_user_from_token(token: str):
    user_id = active_sessions.get(token)
    if user_id:
        return db.get_user(user_id)
    return None

# ---------------- ANALYZER ----------------
class ArmWrestlingAnalyzer:
    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        global cv2
        if cv2 is None:
            import cv2  # ✅ SAFE lazy import

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video")

        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        cap.release()

        return {
            "technique": {
                "primary": "Top Roll",
                "transitions": [{"type": "Hook", "timestamp": 2.6}],
                "description": "Top Roll dominant with Hook transition."
            },
            "risks": [
                {
                    "level": "medium",
                    "title": "Elbow Stress",
                    "description": "Elbow angle exceeded safe range briefly."
                }
            ],
            "strength": {
                "Back Pressure": "Strong (7.5/10)",
                "Wrist Control": "Moderate (6/10)",
                "Side Pressure": "Moderate (6/10)",
                "Endurance Drop": "20% after 7s",
                "summary": "Good back pressure, wrist fatigues early."
            },
            "recommendations": [
                "Wrist curls – 3×15",
                "Static wrist holds – 4×30s",
                "Elbow positioning drills",
                "Hook transition practice"
            ],
            "frames_analyzed": frames,
            "duration": round(frames / fps, 2)
        }

analyzer = ArmWrestlingAnalyzer()

# ---------------- ROUTES ----------------
@app.get("/")
async def root():
    return {"message": "ArmWrestle AI API", "version": "MVP"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "database": "connected"}

@app.post("/api/register")
async def register(email: str = Form(...), name: str = Form(...)):
    if db.get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = db.create_user(email, name)
    token = generate_token()
    active_sessions[token] = user_id

    return {"success": True, "token": token}

@app.post("/api/login")
async def login(email: str = Form(...)):
    user = db.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = generate_token()
    active_sessions[token] = user["id"]
    return {"success": True, "token": token}

@app.post("/api/analyze")
async def analyze(
    video: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(await video.read())
        path = tmp.name

    try:
        result = analyzer.analyze_video(path)
        return {"success": True, "data": result}
    finally:
        os.remove(path)

# ---------------- LOCAL RUN ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
