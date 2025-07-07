from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.orm import relationship


from .base import Base
from .mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    total_quizzes_taken = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    streak = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    firebase_uid = Column(String, unique=True, nullable=True)
    profile_picture = Column(String, nullable=True)
    rate_limit_logs = relationship("RateLimitLog", back_populates="user")
    error_logs = relationship("ErrorLog", back_populates="user")
    # === Relationships ===
    quizzes = relationship("Quiz", back_populates="user", cascade="all, delete-orphan")
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    answers = relationship("UserAnswer", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("SessionLog", back_populates="user", cascade="all, delete-orphan")
    request_logs = relationship("RequestLog", back_populates="user", cascade="all, delete-orphan")
    websocket_sessions = relationship("WebSocketSession", back_populates="user", cascade="all, delete-orphan")
    grading_tasks = relationship("GradingTask", back_populates="user", cascade="all, delete-orphan")
