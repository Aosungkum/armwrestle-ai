from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict, Any
import tempfile
import os
import secrets
try:
    import razorpay
except ImportError:
    razorpay = None
    print("[WARNING] Razorpay not available - payment features disabled")

import hmac
import hashlib
from dotenv import load_dotenv

from database import Database

load_dotenv()

# =========================
# CONFIG
# =========================
ANALYSIS_MODE = "real"   # "mock" or "real"

# Try to import video analyzer
try:
    from video_analyzer import analyze_armwrestling_video
    HAS_REAL_AI = True
    print("[OK] Real video analysis enabled")
except ImportError as e:
    print(f"[WARNING] Could not import video analyzer: {e}")
    print("Falling back to mock analysis")
    HAS_REAL_AI = False
    ANALYSIS_MODE = "mock"
    # Create dummy function for mock mode
    def analyze_armwrestling_video(video_path):
        return {"error": "Video analyzer not available"}

# Razorpay Configuration
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

# Initialize Razorpay client
razorpay_client = None
if razorpay and RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    try:
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    except Exception as e:
        print(f"[WARNING] Failed to initialize Razorpay: {e}")

# Plan pricing (in paise - 1 rupee = 100 paise)
PLAN_PRICES = {
    "pro": 69900,      # ₹699
    "coach": 249900    # ₹2,499
}

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
# STATIC FILES (Frontend)
# =========================
# Try multiple paths to find frontend directory
# Railway deploys from root, so frontend could be at root or in backend/
current_dir = os.getcwd()  # Usually /app on Railway
backend_dir = os.path.dirname(__file__)  # Where api.py is located
root_dir = os.path.dirname(backend_dir) if "backend" in backend_dir else current_dir

possible_frontend_paths = [
    os.path.join(current_dir, "frontend"),  # /app/frontend (if Railway deploys root)
    os.path.join(root_dir, "frontend"),  # Root/frontend
    os.path.join(backend_dir, "frontend"),  # backend/frontend (if copied)
    os.path.join(current_dir, "backend", "frontend"),  # /app/backend/frontend
    "frontend",  # Relative to current dir
    "../frontend",  # One level up
]

frontend_path = None
for path in possible_frontend_paths:
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path) and os.path.isdir(abs_path):
        frontend_path = abs_path
        print(f"[INFO] Found frontend at: {frontend_path}")
        break
    else:
        print(f"[DEBUG] Tried path: {abs_path} (exists: {os.path.exists(abs_path)})")

if frontend_path and os.path.exists(frontend_path):
    # Mount static files (CSS, JS, images)
    try:
        app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    except Exception as e:
        print(f"[WARNING] Could not mount static files: {e}")
    
    # Serve frontend HTML files
    @app.get("/")
    async def serve_index():
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend index.html not found", "mode": ANALYSIS_MODE, "path": frontend_path}
    
    @app.get("/dashboard.html")
    async def serve_dashboard():
        dashboard_path = os.path.join(frontend_path, "dashboard.html")
        if os.path.exists(dashboard_path):
            return FileResponse(dashboard_path)
        raise HTTPException(404, "Dashboard not found")
    
    # Serve frontend JS/CSS files
    @app.get("/{filename:path}")
    async def serve_frontend_file(filename: str):
        # Don't serve API routes as files
        if filename.startswith("api/"):
            raise HTTPException(404, "API route")
        
        file_path = os.path.join(frontend_path, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # If it's an HTML-like request, try index.html (for SPA routing)
        if not "." in filename or filename.endswith(".html"):
            index_path = os.path.join(frontend_path, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
        
        raise HTTPException(404, f"File not found: {filename}")
else:
    # Frontend not found, serve API info
    @app.get("/")
    async def root():
        return {
            "message": "ArmWrestle AI API",
            "mode": ANALYSIS_MODE,
            "note": "Frontend files not found. Tried paths: " + str(possible_frontend_paths),
            "cwd": os.getcwd(),
            "backend_dir": os.path.dirname(__file__)
        }

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/analysis-status")
async def analysis_status():
    """Check if real analysis is available"""
    status = {
        "analysis_mode": ANALYSIS_MODE,
        "has_real_ai": HAS_REAL_AI,
        "dependencies_available": False,
        "error": None
    }
    
    # Test imports
    try:
        import cv2
        import mediapipe
        import numpy
        status["dependencies_available"] = True
        status["opencv_version"] = cv2.__version__
        status["mediapipe_version"] = mediapipe.__version__
    except ImportError as e:
        status["error"] = f"Missing dependencies: {str(e)}"
        status["missing_dependencies"] = []
        try:
            import cv2
        except ImportError:
            status["missing_dependencies"].append("opencv-python")
        try:
            import mediapipe
        except ImportError:
            status["missing_dependencies"].append("mediapipe")
        try:
            import numpy
        except ImportError:
            status["missing_dependencies"].append("numpy")
    
    # Test video analyzer import
    try:
        from video_analyzer import analyze_armwrestling_video
        status["video_analyzer_imported"] = True
    except ImportError as e:
        status["video_analyzer_imported"] = False
        status["video_analyzer_error"] = str(e)
    
    return status

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
    person_id: Optional[int] = Form(None),
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
            try:
                # Real video analysis using MediaPipe and OpenCV
                # person_id: 0 = left person, 1 = right person, None = auto-select first
                print(f"[ANALYSIS] Starting real video analysis... (person_id={person_id})")
                results = analyze_armwrestling_video(tmp_path, person_id=person_id)
                
                # Check if analysis returned an error
                if "error" in results:
                    # Fallback to mock if real analysis fails
                    error_msg = results.get('error', 'Unknown error')
                    print(f"[ERROR] Real analysis failed: {error_msg}, using mock")
                    results = mock_analysis(video.filename)
                    results["_fallback_reason"] = error_msg
                else:
                    technique = results.get('technique', {}).get('primary', 'Unknown')
                    frames = results.get('frames_analyzed', 0)
                    print(f"[SUCCESS] Real analysis completed: {technique} (analyzed {frames} frames)")
                    # Add marker to show it's real analysis
                    results["_is_real_analysis"] = True
            except Exception as e:
                # If real analysis crashes, fallback to mock
                error_msg = str(e)
                print(f"[ERROR] Real analysis exception: {error_msg}, falling back to mock")
                import traceback
                traceback.print_exc()
                results = mock_analysis(video.filename)
                results["_fallback_reason"] = f"Exception: {error_msg}"
        else:
            # Mock analysis (fallback)
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
        # Clean up temporary file
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception as e:
            print(f"Error removing temp file: {e}")

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

# =========================
# RAZORPAY PAYMENT ROUTES
# =========================

@app.post("/api/payment/create-order")
async def create_payment_order(
    plan: str = Form(...),
    authorization: str = Header(...)
):
    """Create a Razorpay order for subscription"""
    if not razorpay or not razorpay_client:
        raise HTTPException(500, "Payment gateway not configured. Razorpay not available.")
    
    token = authorization.replace("Bearer ", "")
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Unauthorized")
    
    if plan not in PLAN_PRICES:
        raise HTTPException(400, "Invalid plan")
    
    amount = PLAN_PRICES[plan]
    
    try:
        # Create Razorpay order
        order_data = {
            "amount": amount,  # Amount in paise
            "currency": "INR",
            "receipt": f"sub_{user['id']}_{plan}_{secrets.token_hex(4)}",
            "notes": {
                "user_id": str(user["id"]),
                "plan": plan,
                "email": user["email"]
            }
        }
        
        order = razorpay_client.order.create(data=order_data)
        
        # Save subscription record
        subscription_id = db.create_subscription(
            user_id=user["id"],
            plan=plan,
            amount=amount,
            razorpay_order_id=order["id"]
        )
        
        return {
            "success": True,
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": RAZORPAY_KEY_ID,
            "subscription_id": subscription_id
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to create order: {str(e)}")

@app.post("/api/payment/verify")
async def verify_payment(
    razorpay_order_id: str = Form(...),
    razorpay_payment_id: str = Form(...),
    razorpay_signature: str = Form(...),
    authorization: str = Header(...)
):
    """Verify Razorpay payment and upgrade user plan"""
    if not razorpay or not razorpay_client:
        raise HTTPException(500, "Payment gateway not configured. Razorpay not available.")
    
    token = authorization.replace("Bearer ", "")
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Unauthorized")
    
    try:
        # Verify payment signature
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        }
        
        # Verify signature
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Update subscription with payment details
        result = db.update_subscription_payment(
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
            status="completed"
        )
        
        if result:
            # Upgrade user plan
            db.update_user_plan(result["user_id"], result["plan"])
            
            # Get updated user
            updated_user = db.get_user(result["user_id"])
            
            return {
                "success": True,
                "message": "Payment verified and plan upgraded successfully",
                "user": updated_user
            }
        else:
            raise HTTPException(400, "Subscription not found")
            
    except Exception as e:
        error_type = type(e).__name__
        if razorpay and hasattr(razorpay, 'errors'):
            try:
                if isinstance(e, razorpay.errors.SignatureVerificationError):
                    raise HTTPException(400, "Invalid payment signature")
            except:
                pass
        if "signature" in str(e).lower() or "SignatureVerification" in error_type:
            raise HTTPException(400, "Invalid payment signature")
        raise HTTPException(400, f"Payment verification failed: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Payment verification failed: {str(e)}")

@app.post("/api/payment/webhook")
async def payment_webhook(request: Request):
    """Handle Razorpay webhook events"""
    if not RAZORPAY_WEBHOOK_SECRET:
        raise HTTPException(500, "Webhook secret not configured")
    
    try:
        body = await request.body()
        headers = dict(request.headers)
        
        # Verify webhook signature
        received_signature = headers.get("x-razorpay-signature", "")
        
        # Calculate expected signature
        expected_signature = hmac.new(
            RAZORPAY_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(received_signature, expected_signature):
            raise HTTPException(400, "Invalid webhook signature")
        
        # Parse webhook payload
        import json
        payload = json.loads(body)
        event = payload.get("event")
        payment_data = payload.get("payload", {}).get("payment", {}).get("entity", {})
        
        if event == "payment.captured":
            order_id = payment_data.get("order_id")
            payment_id = payment_data.get("id")
            
            # Update subscription
            result = db.update_subscription_payment(
                razorpay_order_id=order_id,
                razorpay_payment_id=payment_id,
                razorpay_signature="",  # Not available in webhook
                status="completed"
            )
            
            if result:
                db.update_user_plan(result["user_id"], result["plan"])
        
        return {"success": True, "message": "Webhook processed"}
        
    except Exception as e:
        raise HTTPException(500, f"Webhook processing failed: {str(e)}")

@app.post("/api/upgrade")
async def upgrade_plan(
    plan: str = Form(...),
    authorization: str = Header(...)
):
    """Legacy upgrade endpoint - redirects to payment flow"""
    token = authorization.replace("Bearer ", "")
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(401, "Unauthorized")
    
    # For backward compatibility, return payment order creation endpoint info
    return {
        "success": False,
        "message": "Please use /api/payment/create-order to initiate payment",
        "redirect": "/api/payment/create-order"
    }
