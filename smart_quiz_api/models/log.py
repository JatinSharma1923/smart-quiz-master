
from smart_quiz_api.models.base import Base
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .enum import HealthStatusEnum
from .base import Base


class SessionLog(Base):
    __tablename__ = "session_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    login_time = Column(DateTime, default=datetime.utcnow)
    logout_time = Column(DateTime, nullable=True)
    ip_address = Column(String)
    device_info = Column(String)

    # Relationships
    user = relationship("User", back_populates="sessions")


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    path = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer)
    duration_ms = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="request_logs")


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True)
    error_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship("User")


class APIKey(Base):
    __tablename__ = "api_keys"

    key = Column(String, primary_key=True)
    owner = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    rate_limit = Column(Integer)

    # Relationships
    rate_limit_logs = relationship("RateLimitLog", back_populates="api_key")


class RateLimitLog(Base):
    __tablename__ = "rate_limit_logs"

    id = Column(Integer, primary_key=True)
    ip_address = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    api_key_value = Column(String, ForeignKey("api_keys.key"), nullable=True)
    request_time = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    api_key = relationship("APIKey", back_populates="rate_limit_logs")

class HealthCheckLog(Base):
    __tablename__ = "health_check_logs"

    id = Column(Integer, primary_key=True)
    service = Column(String, nullable=False)
    status = Column(Enum(HealthStatusEnum), nullable=False)
    checked_at = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Float, nullable=True)
    