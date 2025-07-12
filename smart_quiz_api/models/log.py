
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
from datetime import datetime, timezone
from .enum import HealthStatusEnum
from .base import Base


class SessionLog(Base):
    __tablename__ = "session_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    login_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    logout_time = Column(DateTime, nullable=True)
    ip_address = Column(String, nullable=True)
    device_info = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    path = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=True)
    duration_ms = Column(Float, nullable=True)  # type: ignore
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="request_logs")


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True)
    error_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    occurred_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)

    # Relationships
    user = relationship("User", back_populates="error_logs")


class APIKey(Base):
    __tablename__ = "api_keys"

    key = Column(String, primary_key=True)
    owner = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    rate_limit = Column(Integer, nullable=True)

    # Relationships
    rate_limit_logs = relationship("RateLimitLog", back_populates="api_key")


class RateLimitLog(Base):
    __tablename__ = "rate_limit_logs"

    id = Column(Integer, primary_key=True)
    ip_address = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    api_key_value = Column(String, ForeignKey("api_keys.key"), nullable=True, index=True)
    request_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="rate_limit_logs")
    api_key = relationship("APIKey", back_populates="rate_limit_logs")

class HealthCheckLog(Base):
    __tablename__ = "health_check_logs"

    id = Column(Integer, primary_key=True)
    service = Column(String, nullable=False)
    status = Column(Enum(HealthStatusEnum), nullable=False)
    checked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    response_time_ms = Column(Float, nullable=True)  # type: ignore
    