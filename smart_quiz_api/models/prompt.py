from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone

from .base import Base


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    context = Column(String, nullable=True)
    template_text = Column(Text, nullable=False)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PromptCache(Base):
    __tablename__ = "prompt_cache"

    id = Column(Integer, primary_key=True)
    prompt_hash = Column(String, unique=True, nullable=False)
    response_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
