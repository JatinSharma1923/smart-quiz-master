from sqlalchemy import Column, DateTime
from datetime import datetime, timezone


class TimestampMixin:
    """Adds created_at and updated_at timestamps to models."""
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
