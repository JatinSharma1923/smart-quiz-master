import logging
from uuid import uuid4
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from smart_quiz_api.models.user import User  # Adjusted to your structure

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_or_create_user(db: Session, decoded_token: Dict[str, Any]) -> User:
    """
    Get an existing user by Firebase UID or create a new one.
    Updates user info if Firebase fields differ.
    """
    try:
        uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        name = decoded_token.get("name") or ""
        picture = decoded_token.get("picture") or ""

        if not uid or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Firebase token missing required fields (uid, email)"
            )

        user = db.query(User).filter(User.firebase_uid == uid).first()

        if user:
            updated = False

            if email and user.email != email:
                user.email = email
                updated = True
            if name and user.username != name:
                user.username = name
                updated = True
            if picture and user.profile_picture != picture:
                user.profile_picture = picture
                updated = True

            if updated:
                db.commit()
                db.refresh(user)
                logger.info(f"🔁 Updated user info for UID: {uid}")

            return user

        # === Create New User ===
        user = User(
            id=str(uuid4()),
            username=name or email.split("@")[0],
            email=email,
            hashed_password="firebase",  # Dummy value to satisfy nullable=False
            firebase_uid=uid,
            profile_picture=picture
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"🎉 New user created: {email}")

        return user

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ Database error while creating/updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred. Please try again later."
        )


# === Analytics Service ===
def log_quiz_event(quiz_data: Dict[str, Any]) -> None:
    """Log quiz events for analytics."""
    try:
        logger.info(f"📊 Quiz event logged: {quiz_data}")
        # TODO: Store in database or external analytics service
        # This could be expanded to store in RequestLog, ErrorLog, or external service
    except Exception as e:
        logger.error(f"❌ Failed to log quiz event: {e}")


def log_user_activity(user_id: str, activity_type: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Log user activity for analytics."""
    try:
        activity_data: Dict[str, Any] = {
            "user_id": user_id,
            "activity_type": activity_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details if details is not None else {}
        }
        logger.info(f"📈 User activity logged: {activity_data}")
        # TODO: Store in SessionLog or external analytics service
    except Exception as e:
        logger.error(f"❌ Failed to log user activity: {e}")


def get_user_analytics(user_id: str) -> Dict[str, Any]:
    """Get analytics data for a specific user."""
    try:
        # TODO: Implement actual analytics retrieval
        return {
            "user_id": user_id,
            "total_quizzes_taken": 0,
            "average_score": 0.0,
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "streak_days": 0
        }
    except Exception as e:
        logger.error(f"❌ Failed to get user analytics: {e}")
        return {"error": "Failed to retrieve analytics"}
