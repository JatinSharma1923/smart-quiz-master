from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .base import Base
from .mixins import TimestampMixin


class UserAnswer(Base, TimestampMixin):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    selected_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="answers")
    question = relationship("QuizQuestion", back_populates="answers")
