from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import tempfile
import os
import secrets

from database import Database

# =========================
# CONFIG
# =========================
ANALYSIS_MODE = "mock"   # "mock" or "real"
HAS_REAL_AI = False     # Railway-safe (no OpenCV / MediaPipe)

# =========================
# APP INIT
# =========================
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

# =========================
# AUTH HELPERS
# =========================
def generate_token():
    return secrets.token_urlsafe(32)

def get_user_from_token(token: str):
    user_id = active_sessions.get(token)
    if user_id:
        return db.get_user(user_id)
    return None

# =========================
# MOCK ANALYSIS ENGINE
# =========================
def mock_analysis(video_name: str) -> Dict[str, Any]:
    return {
        "technique": {
            "primary": "Top Roll",
            "transitions": [
                {"type": "Hook", "timestamp": 2.3}
            ],
            "description": "Top Roll detected with one transition"
        },
        "risks": [
            {
                "level": "medium",
                "title": "Wrist Exposure",
                "description": "Wrist opened slightly under pressure"
            }
        ],
        "strength": {
            "Back Pressure": "Strong (8.1/10)",
            "Wrist Control": "Moderate (6.2/10)",
            "Side Pressure": "Moderate (6/10)",
            "summary": "Good back pressure, wrist endurance needs improvement"
        },
        "recommendations": [
            "Wrist curls (3x15)",
            "Static wrist holds (4x30s)",
            "Pronation training"
        ],
        "frames_analyzed": 0,
        "duration": 0
    }

# =========================
# ROUTES
# =========================
@app.get("/")
async def root():
    return {
        "message": "ArmWrestle AI API",
        "mode": ANALYSIS_MODE
    }

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/register")
async def register(email: str = Form(...), name: str = Form(...)):
    if db.get_user_by_email(email):
        raise HTTPException(400, "Email already exists")

    user_id = db.create_user(email, name)
    token = generate_token()
    active_sessions[token] = user_id

    user = db.get_user(user_id)

    return {
        "success": True,
        "token": token,
        "user": user
    }

@app.post("/api/login")
async def login(email: str = Form(...)):
    user = db.get_user_by_email(email)
    if not user:
        raise HTTPException(404, "User not found")

    token = generate_token()
    active_sessions[token] = user["id"]
    db.log_action(user["id"], "login")

    return {
        "success": True,
        "token": token,
        "user": user
    }

@app.post("/api/analyze")
async def analyze(
    video: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    user_id = None

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user = get_user_from_token(token)
        if user:
            user_id = user["id"]

    if video.content_type not in [
        "video/mp4", "video/quicktime", "video/x-msvideo"
    ]:
        raise HTTPException(400, "Invalid video format")

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await video.read())
        tmp_path = tmp.name

    try:
        if ANALYSIS_MODE == "real" and HAS_REAL_AI:
            raise HTTPException(501, "Real AI not enabled")
        else:
            results = mock_analysis(video.filename)

        if user_id:
            analysis_id = db.save_analysis(user_id, video.filename, results)
            results["analysis_id"] = analysis_id
            db.log_action(user_id, "analyze")

        return JSONResponse({
            "success": True,
            "data": results
        })

    finally:
        os.remove(tmp_path)

@app.get("/api/history")
async def history(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Unauthorized")

    return {
        "success": True,
        "analyses": db.get_user_analyses(user["id"])
    }

@app.get("/api/stats")
async def stats(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Unauthorized")

    return {
        "success": True,
        "stats": db.get_user_stats(user["id"])
    }
