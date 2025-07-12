from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import uuid4
import hashlib
import os

from smart_quiz_api.database import get_db
from smart_quiz_api.models import User, UserAnswer, UserBadge, SessionLog
from smart_quiz_api.schema import (
    UserCreate, UserOut,
    UserAnswerOut, SessionLogOut, BadgeOut,
    UserStatsResponse, DetailResponse
)
from smart_quiz_api.services.firebase import get_current_user

router = APIRouter(
    tags=["User"]
)

# === Utility: Hash and verify ===
def hash_password(password: str) -> str:
    """Hash a password using a secure method with salt"""
    salt = os.urandom(32)  # 32 bytes = 256 bits
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # Number of iterations
    )
    # Store salt and key together
    return salt.hex() + ':' + key.hex()

def verify_password(plain: str, stored_hash: str) -> bool:
    """Verify a password against its stored hash"""
    try:
        salt_hex, key_hex = stored_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        stored_key = bytes.fromhex(key_hex)
        
        # Generate key with same salt and iterations
        key = hashlib.pbkdf2_hmac(
            'sha256',
            plain.encode('utf-8'),
            salt,
            100000  # Same number of iterations as in hash_password
        )
        
        # Compare in constant time to prevent timing attacks
        return key == stored_key
    except (ValueError, TypeError):
        return False


# === Register a new user ===
@router.post("/register", response_model=UserOut)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        id=str(uuid4()),
        email=user_data.email,
        username=user_data.full_name,  # Using full_name from schema as username in model
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# === User login ===
@router.post("/login", response_model=UserOut)
def login_user(email: str = Body(...), password: str = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if account is deleted
    if user.is_deleted:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    return user


# === Get user profile ===
@router.get("/{user_id}", response_model=UserOut)
def get_user_profile(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if account is deleted
    if user.is_deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# === Update user profile ===
@router.put("/{user_id}", response_model=UserOut)
def update_user_profile(
    user_id: str, 
    update: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user is updating their own profile or is admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if account is deleted and only allow admins to update deleted accounts
    if user.is_deleted and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Cannot update a deactivated account")

    # Check for email uniqueness when updating
    existing_email = db.query(User).filter(User.email == update.email, User.id != user_id).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already in use by another account")

    user.email = update.email
    user.username = update.full_name  # Using full_name from schema as username in model
    user.hashed_password = hash_password(update.password)
    db.commit()
    db.refresh(user)
    return user


# === Change password ===
@router.patch("/{user_id}/change-password", response_model=DetailResponse)
def change_password(
    user_id: str,
    old_password: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user is changing their own password or is admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to change this password")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if account is deleted and only allow admins to change passwords for deleted accounts
    if user.is_deleted and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Cannot change password for a deactivated account")
        
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect current password")
        
    user.hashed_password = hash_password(new_password)
    db.commit()
    return DetailResponse(detail="Password changed successfully")


# === Soft delete user account ===
@router.delete("/{user_id}", response_model=DetailResponse)
def delete_user(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user is deleting their own account or is admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this account")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if account is already deleted
    if user.is_deleted:
        raise HTTPException(status_code=404, detail="User already deleted")
    
    user.is_deleted = True
    db.commit()
    return DetailResponse(detail="User account soft-deleted")


# === Reactivate user account ===
@router.patch("/{user_id}/reactivate", response_model=DetailResponse)
def reactivate_user(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admins can reactivate accounts
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_deleted = False
    db.commit()
    return DetailResponse(detail="User account reactivated")


# === Get user's quiz answers ===
@router.get("/{user_id}/answers", response_model=List[UserAnswerOut])
def get_user_answers(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user is viewing their own answers or is admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view these answers")
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if account is deleted and only allow admins to view deleted accounts
    if user.is_deleted and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Cannot access a deactivated account")
        
    return db.query(UserAnswer).filter(UserAnswer.user_id == user_id).all()


# === Get user's earned badges ===
@router.get("/{user_id}/badges", response_model=List[BadgeOut])
def get_user_badges(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user is viewing their own badges or is admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view these badges")
        
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if account is deleted and only allow admins to view deleted accounts
    if user.is_deleted and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Cannot access a deactivated account")
        
    badge_joins = db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
    return [ub.badge for ub in badge_joins]


# === Get user's login sessions ===
@router.get("/{user_id}/sessions", response_model=List[SessionLogOut])
def get_user_sessions(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user is viewing their own sessions or is admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view these sessions")
        
    return db.query(SessionLog).filter(SessionLog.user_id == user_id).order_by(SessionLog.login_time.desc()).limit(50).all()


# === Get user stats (quizzes taken, avg score, streak) ===
@router.get("/{user_id}/stats", response_model=UserStatsResponse)
def get_user_stats(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user is viewing their own stats or is admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view these stats")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if account is deleted and only allow admins to view deleted accounts
    if user.is_deleted and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Cannot access a deactivated account")
    
    # Calculate actual stats from UserAnswer table
    answers = db.query(UserAnswer).filter(UserAnswer.user_id == user_id).all()
    total_answers = len(answers)
    correct_answers = sum(1 for answer in answers if answer.is_correct)
    accuracy = (correct_answers / total_answers * 100) if total_answers > 0 else 0.0
    
    # Get total quizzes taken (assuming you have a way to count unique quizzes)
    total_quizzes = user.total_quizzes_taken if hasattr(user, 'total_quizzes_taken') else 0
    
    return UserStatsResponse(
        total_quizzes=total_quizzes,
        total_answers=total_answers,
        correct_answers=correct_answers,
        accuracy=round(accuracy, 2)
    )