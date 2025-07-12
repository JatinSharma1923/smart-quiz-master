from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
from smart_quiz_api.database import get_db
from smart_quiz_api.schema import (
    FeedbackOut, ErrorLogOut, SessionLogOut, GradingTaskOut,
    APIKeyOut, HealthCheckLogOut, PromptCacheOut, LogOut,
    CacheClearResponse, RedisStatsResponse, OpenAIStatusResponse
)
from smart_quiz_api.models import (
    Feedback, ErrorLog, SessionLog, GradingTask, APIKey,
    HealthCheckLog, PromptCache, User, Quiz, RequestLog
)
from dotenv import load_dotenv
from smart_quiz_api.services.firebase import get_current_user
from smart_quiz_api.services.redis_service import redis_service
from smart_quiz_api.config import settings

def verify_admin_user(user: User = Depends(get_current_user)):
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admins only")
    return user


# === Load env variables ===
load_dotenv()
ADMIN_API_KEY = settings.admin_api_key

# === Security Dependency ===
def verify_admin_key(x_admin_key: str = Header(..., alias=settings.api_key_header)):
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized access to admin routes")

# === Router Setup with global dependency ===
router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(verify_admin_key)]
)

# === System Stats ===
@router.get("/stats", response_model=dict,dependencies=[Depends(verify_admin_user)])
def get_stats(db: Session = Depends(get_db)):
    return {
        "total_users": db.query(User).count(),
        "total_quizzes": db.query(Quiz).count(),
        "total_feedback": db.query(Feedback).count(),
        "total_errors": db.query(ErrorLog).count(),
        "grading_tasks": db.query(GradingTask).count(),
        "sessions": db.query(SessionLog).count()
    }

# === Feedback Logs ===
@router.get("/feedbacks", response_model=List[FeedbackOut])
def list_feedbacks(db: Session = Depends(get_db)):
    return db.query(Feedback).order_by(Feedback.submitted_on.desc()).limit(100).all()

# === Error Logs ===
@router.get("/errors", response_model=List[ErrorLogOut])
def list_errors(db: Session = Depends(get_db)):
    return db.query(ErrorLog).order_by(ErrorLog.occurred_at.desc()).limit(100).all()

# === Session Logs ===
@router.get("/sessions", response_model=List[SessionLogOut])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(SessionLog).order_by(SessionLog.login_time.desc()).limit(100).all()

# === Grading Tasks ===
@router.get("/grading-tasks", response_model=List[GradingTaskOut])
def list_grading_tasks(db: Session = Depends(get_db)):
    return db.query(GradingTask).order_by(GradingTask.started_at.desc()).limit(100).all()

# === API Keys ===
@router.get("/api-keys", response_model=List[APIKeyOut])
def list_api_keys(db: Session = Depends(get_db)):
    return db.query(APIKey).order_by(APIKey.created_at.desc()).all()

# === Toggle API Key ===
@router.patch("/api-keys/{key}/toggle", response_model=APIKeyOut)
def toggle_api_key(key: str, db: Session = Depends(get_db)):
    api_key = db.query(APIKey).filter(APIKey.key == key).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    setattr(api_key, "is_active", not getattr(api_key, "is_active", True))
    db.commit()
    db.refresh(api_key)
    return api_key

# === Health Check Logs ===
@router.get("/health", response_model=List[HealthCheckLogOut])
def get_health_logs(db: Session = Depends(get_db)):
    return db.query(HealthCheckLog).order_by(HealthCheckLog.checked_at.desc()).limit(50).all()

# === Prompt Cache ===
@router.get("/prompt-cache", response_model=List[PromptCacheOut])
def get_prompt_cache(db: Session = Depends(get_db)):
    return db.query(PromptCache).order_by(PromptCache.created_at.desc()).limit(100).all()

# === Request Logs ===
@router.get("/requests", response_model=List[LogOut])
def get_request_logs(db: Session = Depends(get_db)):
    return db.query(RequestLog).order_by(RequestLog.timestamp.desc()).limit(100).all()

# === Clear Redis Cache ===
@router.delete("/cache/clear", response_model=CacheClearResponse)
def clear_redis_cache():
    if redis_service.flush_db():
        return CacheClearResponse(message="Redis cache cleared successfully.")
    return CacheClearResponse(message="Failed to clear cache")

# === Redis Stats ===
@router.get("/redis/stats", response_model=RedisStatsResponse)
def get_redis_stats():
    stats = redis_service.get_stats()
    return RedisStatsResponse(**stats)

# === OpenAI Status Test ===
@router.get("/openai/status", response_model=OpenAIStatusResponse)
def openai_status_check():
    try:
        from openai import OpenAI
        client = OpenAI()
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, are you online?"}]
        )
        return OpenAIStatusResponse(model="gpt-3.5-turbo", status="online", latency_ms=0.0)
    except Exception:
        return OpenAIStatusResponse(model="gpt-3.5-turbo", status="offline", latency_ms=0.0)
