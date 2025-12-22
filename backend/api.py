from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
import numpy as np
from typing import Optional, Dict, Any
from database import Database
import secrets

# -------- SAFE LAZY IMPORT PLACEHOLDERS --------
cv2 = None   # OpenCV will be imported ONLY when needed

# -------- APP SETUP --------
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

# -------- HELPERS --------
def generate_token():
    return secrets.token_urlsafe(32)

def get_user_from_token(token: str):
    user_id = active_sessions.get(token)
    if user_id:
        return db.get_user(user_id)
    return None

# -------- ANALYZER (SAFE MVP MODE) --------
class ArmWrestlingAnalyzer:
    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        global cv2
        if cv2 is None:
            import cv2  # lazy import (prevents Railway crash)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video")

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        cap.release()

        # ---- MOCK BUT REALISTIC ANALYSIS ----
        return {
            "technique": {
                "primary": "Top Roll",
                "transitions": [
                    {"type": "Hook", "timestamp": 2.4}
                ],
                "description": "Primary technique: Top Roll with mid-match Hook transition."
            },
            "risks": [
                {
                    "level": "medium",
                    "title": "Elbow Stress",
                    "description": "Elbow angle exceeded recommended range briefly."
                }
            ],
            "strength": {
                "Back Pressure": "Strong (7.8/10)",
                "Wrist Control": "Moderate (6.2/10)",
                "Side Pressure": "Moderate (6/10)",
                "Endurance Drop": "22% after 7 seconds",
                "summary": "Good back pressure, wrist weakened under pronation."
            },
            "recommendations": [
                "Wrist curls – 3×15",
                "Static wrist holds – 4×30s",
                "Elbow positioning drills",
                "Hook transition practice"
            ],
            "frames_analyzed": frame_count,
            "duration": round(frame_count / fps, 2)
        }

analyzer = ArmWrestlingAnalyzer()

# -------- ROUTES --------
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

    user = db.get_user(user_id)
    return {"success": True, "token": token, "user": user}

@app.post("/api/login")
async def login(email: str = Form(...)):
    user = db.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = generate_token()
    active_sessions[token] = user["id"]
    db.log_action(user["id"], "login")

    return {"success": True, "token": token, "user": user}

@app.post("/api/analyze")
async def analyze(
    video: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    user = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user = get_user_from_token(token)

    if video.content_type not in ["video/mp4", "video/quicktime", "video/x-msvideo"]:
        raise HTTPException(status_code=400, detail="Invalid video type")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(await video.read())
        tmp_path = tmp.name

    try:
        result = analyzer.analyze_video(tmp_path)

        if user:
            analysis_id = db.save_analysis(user["id"], video.filename, result)
            result["analysis_id"] = analysis_id

        return JSONResponse(content={"success": True, "data": result})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        os.remove(tmp_path)

@app.get("/api/history")
async def history(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {"success": True, "analyses": db.get_user_analyses(user["id"])}

@app.get("/api/stats")
async def stats(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {
        "success": True,
        "stats": db.get_user_stats(user["id"]),
        "plan": user["plan"]
    }

@app.post("/api/upgrade")
async def upgrade(plan: str = Form(...), authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db.update_user_plan(user["id"], plan)
    return {"success": True, "plan": plan}

# -------- LOCAL RUN --------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
