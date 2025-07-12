# smart_quiz_api/main.py
# Smart Quiz Master API - Main Application File
from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security.api_key import APIKeyHeader
from fastapi.websockets import WebSocket
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_429_TOO_MANY_REQUESTS
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response
import logging
import time
from typing import Callable, Awaitable, Any, Dict
from contextlib import asynccontextmanager

# Import configuration
from smart_quiz_api.config import settings

# Logging Setup
logging.basicConfig(
    level=logging.INFO,  # Optionally use a log_level field if you add it to config
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 API server is starting up...")
    
    # Initialize services
    from smart_quiz_api.services import initialize_services
    try:
        initialize_services()
        logger.info("✅ Services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("🛑 API server is shutting down...")

# App Initialization
app = FastAPI(
    title=settings.app_name, 
    version=settings.app_version, 
    lifespan=lifespan,
    debug=False  # Optionally use a debug field if you add it to config
)

# Import Routers
from smart_quiz_api.routers.quiz_router import router as quiz_router
from smart_quiz_api.routers.user_router import router as user_router
from smart_quiz_api.routers.admin_router import router as admin_router

# Include Routers
app.include_router(quiz_router, prefix="/quiz", tags=["Quiz"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Optionally use a cors_allowed_origins field if you add it to config
    allow_credentials=True,  # Optionally use a cors_allow_credentials field if you add it to config
    allow_methods=["*"],    # Optionally use a cors_allowed_methods field if you add it to config
    allow_headers=["*"],    # Optionally use a cors_allowed_headers field if you add it to config
)

# API Key Auth Middleware for AI Routes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)  # Optionally use api_key_header from config

def verify_api_key(x_api_key: str = Header(..., alias=settings.api_key_header)):
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")

# Import Services
from smart_quiz_api.services.firebase import simple_limiter

# Rate Limiting Middleware
@app.middleware("http")
async def enforce_rate_limit(request: Request, call_next: Callable[[StarletteRequest], Awaitable[Response]]) -> Response:
    if not settings.enable_rate_limiting:
        return await call_next(request)
    
    client_ip = request.client.host if request.client else "unknown"
    if not simple_limiter.allow_request(client_ip):
        return JSONResponse(status_code=HTTP_429_TOO_MANY_REQUESTS, content={"detail": "Rate limit exceeded"})
    return await call_next(request)

# Logging Request Time Middleware
@app.middleware("http")
async def log_request_time(request: Request, call_next: Callable[[StarletteRequest], Awaitable[Response]]) -> Response:
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Request to {request.url.path} took {duration:.3f}s")
    return response

# Exception Logging Middleware
@app.middleware("http")
async def add_exception_logging(request: Request, call_next: Callable[[StarletteRequest], Awaitable[Response]]) -> Response:
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.exception(f"Unhandled error: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# Health Check Route
@app.get("/")
async def root():
    return {"message": "✅ Smart Quiz Master API is running!"}

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint."""
    from smart_quiz_api.services import health_check as service_health_check
    from smart_quiz_api.config import settings

    services_status: Dict[str, Any] = service_health_check() or {}
    overall_status = services_status.get("overall", "unknown")

    health_data: Dict[str, Any] = {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "services": services_status,
        "config": {
            "ai_features_enabled": settings.enable_ai_features,
            "websockets_enabled": settings.enable_websockets,
            "caching_enabled": settings.enable_caching,
            "rate_limiting_enabled": settings.enable_rate_limiting
        }
    }

    # Determine overall status
    if overall_status == "unhealthy":
        health_data["status"] = "unhealthy"
    elif overall_status == "degraded":
        health_data["status"] = "degraded"
    elif overall_status == "unknown":
        health_data["status"] = "unknown"

    return health_data

# Auto-Grading Logic + Background Task Logging
@app.post("/quiz/submit")
async def submit_quiz(quiz_data: dict[str, Any]):
    # TODO: Replace below with real grading logic
    return {"result": "Quiz submitted and being graded"}

# AI Prompt Generation + Caching + Template Rendering
@app.get("/ai/question")
async def get_ai_question(prompt: str, api_key: str = Depends(verify_api_key)) -> dict[str, Any]:
    # TODO: Replace with proper caching and OpenAI integration
    ai_result = f"[AI RESPONSE for: {prompt}]"  # Placeholder for actual OpenAI call
    
    return {
        "cached": False, 
        "result": ai_result,
        "prompt": prompt,
        "timestamp": time.time()
    }

# WebSocket for Real-Time Multiplayer (Phase 2)
@app.websocket("/ws/quiz")
async def websocket_quiz(websocket: WebSocket):
    if not settings.enable_websockets:
        await websocket.close(code=1008, reason="WebSockets disabled")
        return
    
    await websocket.accept()
    await websocket.send_text("🔌 Connected to Real-Time Quiz")
    await websocket.close()

# Global Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()} at {request.url}")
    return JSONResponse(status_code=HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors(), "body": exc.body})

@app.get("/secure-endpoint", dependencies=[Depends(verify_api_key)])
async def secure_endpoint():
    return {"message": "You have access!"}

