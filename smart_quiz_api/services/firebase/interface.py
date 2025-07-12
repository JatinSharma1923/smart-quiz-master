from fastapi import Request
from sqlalchemy.orm import Session
from typing import Optional

from .firebase_auth import (
    get_current_user as _get_current_user,
    get_current_user_optional as _get_current_user_optional,
    require_admin as _require_admin
)
from smart_quiz_api.models import User


def get_authenticated_user(request: Request, db: Session) -> User:
    """
    Wrapper function to get the current authenticated user (non-dependency style).
    """
    return _get_current_user(request=request, db=db)

def get_authenticated_user_optional(request: Request, db: Session) -> Optional[User]:
    """
    Wrapper function to optionally get the authenticated user (returns None if not valid).
    """
    return _get_current_user_optional(request=request, db=db)

def enforce_admin_user(user: User) -> User:
    """
    Wrapper to validate if the user has admin privileges.
    """
    return _require_admin(current_user=user)




# === Rate Limiter ===
from fastapi.responses import JSONResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import time
from typing import Dict, List

# Placeholder for slowapi limiter (if needed in future)
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
# limiter = Limiter(key_func=get_remote_address)

# Simple rate limiter for fallback
class SimpleRateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
        self.max_requests = 100  # requests per window
        self.window_seconds = 3600  # 1 hour window
    
    def allow_request(self, client_ip: str) -> bool:
        """Check if request is allowed based on rate limiting."""
        current_time = time.time()
        
        # Clean old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < self.window_seconds
            ]
        else:
            self.requests[client_ip] = []
        
        # Check if under limit
        if len(self.requests[client_ip]) < self.max_requests:
            self.requests[client_ip].append(current_time)
            return True
        
        return False

# Global simple rate limiter instance
simple_limiter = SimpleRateLimiter()

# Custom error handler for rate limiting
def rate_limit_exceeded_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )