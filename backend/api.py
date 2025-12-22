# FORCE_REBUILD_2025_02

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
from database import Database

app = FastAPI(title="ArmWrestle AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()

@app.get("/")
def root():
    return {"status": "ArmWrestle AI Backend LIVE"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}

@app.post("/api/analyze")
async def analyze(video: UploadFile = File(...)):
    if not video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid video")

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await video.read())
        path = tmp.name

    # MOCK ANALYSIS (Railway-safe)
    result = {
        "technique": "Top Roll",
        "risk": "Medium elbow stress",
        "recommendations": [
            "Wrist curls",
            "Static holds",
            "Better elbow positioning"
        ]
    }

    os.remove(path)

    return JSONResponse({"success": True, "data": result})
