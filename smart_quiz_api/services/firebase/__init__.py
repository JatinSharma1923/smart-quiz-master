from .interface import rate_limit_exceeded_handler, simple_limiter
from .initialize import initialize_firebase
from .firebase_auth import get_current_user, get_current_user_optional, require_admin
from .health import check_firebase_health
from .user import get_or_create_user, log_quiz_event, log_user_activity, get_user_analytics
from .utils import extract_token_from_header, verify_firebase_token
initialize_firebase()

__all__ = [
    "get_current_user",
    "get_current_user_optional",
    "require_admin",
    "check_firebase_health",
    "get_or_create_user",
    "extract_token_from_header",
    "verify_firebase_token",
    "rate_limit_exceeded_handler",
    "simple_limiter",
    "log_quiz_event",
    "log_user_activity",
    "get_user_analytics",
]
