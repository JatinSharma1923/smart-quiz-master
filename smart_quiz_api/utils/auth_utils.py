# smart_quiz_api/utils/auth_utils.py

import firebase_admin  # type: ignore
from firebase_admin import auth, credentials  # type: ignore
from fastapi import HTTPException, status
from typing import Dict, Optional
from smart_quiz_api.utils.logger import logger

# This assumes firebase_admin.initialize_app() is called somewhere globally

def verify_token(id_token: str) -> Dict[str, str]:
    """Verify Firebase ID token and return decoded claims."""
    try:
        if not id_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No token provided"
            )
        
        decoded = auth.verify_id_token(id_token)  # type: ignore
        logger.info(f"Token verified for user: {decoded.get('email', 'unknown')}")  # type: ignore
        return decoded  # type: ignore
    except auth.ExpiredIdTokenError:  # type: ignore
        logger.warning("Expired token attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except auth.RevokedIdTokenError:  # type: ignore
        logger.warning("Revoked token attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    except auth.InvalidIdTokenError:  # type: ignore
        logger.warning("Invalid token attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )

def get_user_email(decoded_token: Dict[str, str]) -> str:
    """Extract user email from decoded token."""
    return decoded_token.get("email", "unknown@user.com")

def get_user_id(decoded_token: Dict[str, str]) -> str:
    """Extract user ID from decoded token."""
    return decoded_token.get("user_id", decoded_token.get("uid", "unknown"))

def is_admin_user(decoded_token: Dict[str, str]) -> bool:
    """Check if user has admin privileges."""
    return bool(decoded_token.get("admin", False)) or decoded_token.get("role") == "admin"

def validate_quiz_access(user_id: str, quiz_user_id: str, is_admin: bool = False) -> bool:
    """Validate if user has access to a specific quiz."""
    if is_admin:
        return True
    return user_id == quiz_user_id

def log_auth_attempt(user_email: str, success: bool, context: Optional[str] = None):
    """Log authentication attempts for security monitoring."""
    auth_status = "✅ Success" if success else "❌ Failed"
    context_str = f" [{context}]" if context else ""
    logger.info(f"🔐 Auth {auth_status} - User: {user_email}{context_str}")
