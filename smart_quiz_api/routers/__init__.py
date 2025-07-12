from .quiz_router import router as quiz_router
from .user_router import router as user_router
from .admin_router import router as admin_router

__all__ = ["quiz_router", "user_router", "admin_router"]
