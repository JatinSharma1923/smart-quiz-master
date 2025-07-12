from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from smart_quiz_api.services.firebase.utils import extract_token_from_header, verify_firebase_token
from smart_quiz_api.services.firebase.user import get_or_create_user
from smart_quiz_api.database import get_db
from smart_quiz_api.models import User

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to extract and authenticate a user via Firebase token.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    token = extract_token_from_header(auth_header)
    decoded_token = verify_firebase_token(token)
    return get_or_create_user(db, decoded_token)

def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency that tries to get user, but returns None if auth fails.
    """
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None

def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to require admin privileges.
    """
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
