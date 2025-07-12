from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy.orm import relationship


from .base import Base
from .mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    total_quizzes_taken = Column(Integer, default=0, nullable=False)
    average_score = Column(Float, default=0.0, nullable=False)  # type: ignore
    streak = Column(Integer, default=0, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    firebase_uid = Column(String, unique=True, nullable=True, index=True)
    profile_picture = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    # === Relationships ===
    quizzes = relationship("Quiz", back_populates="user", cascade="all, delete-orphan")
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    answers = relationship("UserAnswer", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("SessionLog", back_populates="user")
    request_logs = relationship("RequestLog", back_populates="user")
    websocket_sessions = relationship("WebSocketSession", back_populates="user")
    grading_tasks = relationship("GradingTask", back_populates="user")
    rate_limit_logs = relationship("RateLimitLog", back_populates="user")
    error_logs = relationship("ErrorLog", back_populates="user")
