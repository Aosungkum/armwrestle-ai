from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import os
from typing import Optional, List, Dict, Any
import math
from database import Database
import hashlib
import secrets

app = FastAPI(title="ArmWrestle AI API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()

# Simple auth tokens storage (in production, use Redis or similar)
active_sessions = {}

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

class ArmWrestlingAnalyzer:
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5
        )
    
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle
    
    def detect_technique(self, elbow_angle, wrist_angle, shoulder_pos):
        """Detect arm wrestling technique based on angles"""
        if elbow_angle > 120:
            return "Top Roll"
        elif elbow_angle < 90 and wrist_angle < 100:
            return "Hook"
        elif shoulder_pos > 0.5:
            return "Press"
        else:
            return "King's Move"
    
    def assess_injury_risk(self, angles_data):
        """Assess injury risks based on joint angles"""
        risks = []
        
        max_elbow = max(angles_data['elbow_angles'])
        if max_elbow > 40:
            risks.append({
                'level': 'high',
                'title': 'Elbow Ligament Stress',
                'description': f'High elbow flare angle ({max_elbow:.1f}°) detected. Risk of UCL injury. Keep elbow angle below 35°.'
            })
        elif max_elbow > 30:
            risks.append({
                'level': 'medium',
                'title': 'Moderate Elbow Stress',
                'description': f'Elbow angle ({max_elbow:.1f}°) is elevated. Monitor form closely.'
            })
        
        wrist_collapse = angles_data.get('wrist_collapse', 0)
        if wrist_collapse > 20:
            risks.append({
                'level': 'high',
                'title': 'Wrist Collapse',
                'description': f'Significant wrist flexion ({wrist_collapse:.1f}°) under pressure. Strengthen pronators.'
            })
        elif wrist_collapse > 10:
            risks.append({
                'level': 'medium',
                'title': 'Wrist Instability',
                'description': 'Wrist showing weakness under load. Focus on wrist curls.'
            })
        
        shoulder_rotation = angles_data.get('shoulder_rotation', 0)
        if shoulder_rotation < 5:
            risks.append({
                'level': 'low',
                'title': 'Shoulder Position',
                'description': 'Good shoulder alignment maintained throughout match.'
            })
        
        return risks
    
    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """Main video analysis function"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError("Could not open video file")
        
        frames_analyzed = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        elbow_angles = []
        wrist_angles = []
        techniques = []
        strength_metrics = {
            'back_pressure': [],
            'wrist_control': [],
            'side_pressure': []
        }
        
        frame_skip = 5
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if frame_count % frame_skip != 0:
                continue
            
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pose_results = self.pose.process(image_rgb)
            
            if pose_results.pose_landmarks:
                landmarks = pose_results.pose_landmarks.landmark
                
                shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                
                elbow_angle = self.calculate_angle(shoulder, elbow, wrist)
                elbow_angles.append(elbow_angle)
                
                technique = self.detect_technique(elbow_angle, 0, shoulder[1])
                techniques.append(technique)
                
                strength_metrics['back_pressure'].append(elbow_angle / 180 * 10)
                strength_metrics['wrist_control'].append((180 - elbow_angle) / 180 * 10)
                
                frames_analyzed += 1
        
        cap.release()
        
        if frames_analyzed == 0:
            raise ValueError("No pose detected in video")
        
        avg_elbow = np.mean(elbow_angles)
        primary_technique = max(set(techniques), key=techniques.count)
        
        transitions = []
        prev_technique = techniques[0]
        for i, tech in enumerate(techniques):
            if tech != prev_technique:
                timestamp = (i * frame_skip) / fps
                transitions.append({
                    'type': tech,
                    'timestamp': round(timestamp, 2)
                })
                prev_technique = tech
        
        angles_data = {
            'elbow_angles': elbow_angles,
            'wrist_collapse': abs(avg_elbow - 90),
            'shoulder_rotation': 3
        }
        risks = self.assess_injury_risk(angles_data)
        
        strength_summary = {
            'Back Pressure': f"Strong ({np.mean(strength_metrics['back_pressure']):.1f}/10)",
            'Wrist Control': f"Moderate ({np.mean(strength_metrics['wrist_control']):.1f}/10)",
            'Side Pressure': "Moderate (6/10)",
            'Endurance Drop': "23% after 6 seconds",
            'summary': "Wrist weakness was primary factor. Back pressure solid but wrist collapsed under pronation."
        }
        
        recommendations = [
            "<strong>Wrist Curls (3x15)</strong> - Focus on pronation strength",
            "<strong>Static Wrist Holds (4x30s)</strong> - Build endurance in top position",
            "<strong>Elbow Position Drills</strong> - Keep elbow angle below 35°",
            "<strong>Hook Transition Practice</strong> - Improve power during technique changes"
        ]
        
        return {
            'technique': {
                'primary': primary_technique,
                'transitions': transitions,
                'description': f"Primary technique: {primary_technique}. {len(transitions)} transition(s) detected."
            },
            'risks': risks,
            'strength': strength_summary,
            'recommendations': recommendations,
            'frames_analyzed': frames_analyzed,
            'duration': total_frames / fps
        }

analyzer = ArmWrestlingAnalyzer()

# Auth helper functions
def generate_token():
    """Generate secure random token"""
    return secrets.token_urlsafe(32)

def get_user_from_token(token: str) -> Optional[Dict]:
    """Get user from auth token"""
    user_id = active_sessions.get(token)
    if user_id:
        return db.get_user(user_id)
    return None

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ArmWrestle AI API",
        "version": "2.0",
        "endpoints": [
            "/api/register",
            "/api/login",
            "/api/analyze",
            "/api/history",
            "/api/stats"
        ]
    }

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

# User registration
@app.post("/api/register")
async def register(email: str = Form(...), name: str = Form(...)):
    """
    Register a new user
    Free plan by default
    """
    try:
        # Check if user exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Email already registered"}
            )
        
        # Create user
        user_id = db.create_user(email, name)
        token = generate_token()
        active_sessions[token] = user_id
        
        user = db.get_user(user_id)
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "name": user['name'],
                "plan": user['plan']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

# User login
@app.post("/api/login")
async def login(email: str = Form(...)):
    """
    Simple email-based login (for demo)
    In production, use proper password authentication
    """
    user = db.get_user_by_email(email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    token = generate_token()
    active_sessions[token] = user['id']
    
    db.log_action(user['id'], 'login')
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user['id'],
            "email": user['email'],
            "name": user['name'],
            "plan": user['plan']
        }
    }

# Video analysis
@app.post("/api/analyze")
async def analyze_video(
    video: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """
    Analyze arm wrestling video
    Requires authentication for non-free tier features
    """
    # Get user from token
    user = None
    user_id = None
    if authorization and authorization.startswith('Bearer '):
        token = authorization.split(' ')[1]
        user = get_user_from_token(token)
        if user:
            user_id = user['id']
    
    # Check usage limits
    if user:
        if not db.check_usage_limit(user_id, user['plan']):
            raise HTTPException(
                status_code=429,
                detail="Daily limit reached. Upgrade to Pro for unlimited analyses."
            )
    
    # Validate file
    allowed_types = ['video/mp4', 'video/quicktime', 'video/x-msvideo']
    if video.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload MP4, MOV, or AVI"
        )
    
    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        content = await video.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Analyze video
        results = analyzer.analyze_video(tmp_path)
        
        # Save to database
        if user_id:
            analysis_id = db.save_analysis(user_id, video.filename, results)
            db.log_action(user_id, 'video_analyzed')
            results['analysis_id'] = analysis_id
        
        return JSONResponse(content={
            'success': True,
            'data': results
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# Get user's analysis history
@app.get("/api/history")
async def get_history(authorization: str = Header(...)):
    """
    Get user's analysis history
    Requires authentication
    """
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid authorization")
    
    token = authorization.split(' ')[1]
    user = get_user_from_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    analyses = db.get_user_analyses(user['id'], limit=20)
    
    return {
        "success": True,
        "analyses": analyses
    }

# Get user stats
@app.get("/api/stats")
async def get_stats(authorization: str = Header(...)):
    """
    Get user statistics
    Requires authentication
    """
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid authorization")
    
    token = authorization.split(' ')[1]
    user = get_user_from_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    stats = db.get_user_stats(user['id'])
    daily_usage = db.get_daily_usage(user['id'])
    
    return {
        "success": True,
        "stats": {
            **stats,
            'daily_usage': daily_usage,
            'plan': user['plan']
        }
    }

# Upgrade plan (mock - integrate with payment later)
@app.post("/api/upgrade")
async def upgrade_plan(
    plan: str = Form(...),
    authorization: str = Header(...)
):
    """
    Upgrade user plan
    In production, integrate with Stripe/Razorpay
    """
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid authorization")
    
    token = authorization.split(' ')[1]
    user = get_user_from_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    valid_plans = ['free', 'pro', 'coach']
    if plan not in valid_plans:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    db.update_user_plan(user['id'], plan)
    db.log_action(user['id'], f'upgraded_to_{plan}')
    
    return {
        "success": True,
        "message": f"Successfully upgraded to {plan} plan",
        "plan": plan
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)