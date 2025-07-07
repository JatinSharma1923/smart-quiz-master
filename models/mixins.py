from sqlalchemy import Column, DateTime
from datetime import datetime


class TimestampMixin:
    """Adds created_at and updated_at timestamps to models."""
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
