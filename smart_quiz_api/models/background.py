# smart_quiz_api/models/websocket.py
from .mixins import TimestampMixin
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base
from .enum import TaskStatusEnum, GradingStatusEnum


class BackgroundTaskQueue(Base):
    __tablename__ = "background_tasks"

    id = Column(Integer, primary_key=True)
    task_name = Column(String, nullable=False)
    payload = Column(Text, nullable=False)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class WebSocketSession(Base):
    __tablename__ = "websocket_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    connection_time = Column(DateTime, default=datetime.utcnow)
    disconnect_time = Column(DateTime, nullable=True)
    client_ip = Column(String)

    # Relationships
    user = relationship("User", back_populates="websocket_sessions")


class GradingTask(Base):
    __tablename__ = "grading_tasks"

    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(GradingStatusEnum), default=GradingStatusEnum.pending)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text)

    # Relationships
    quiz = relationship("Quiz", back_populates="grading_tasks")
    user = relationship("User", back_populates="grading_tasks")

