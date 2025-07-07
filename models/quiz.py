from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base
from .mixins import TimestampMixin
from .enum import DifficultyEnum, QuestionTypeEnum


class Quiz(Base, TimestampMixin):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=True)
    difficulty = Column(Enum(DifficultyEnum), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    source_url = Column(String, nullable=True)
    scraped_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="quiz", cascade="all, delete-orphan")
    grading_tasks = relationship("GradingTask", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base, TimestampMixin):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(String, nullable=False)
    options = Column(String, nullable=False)  # Stored as JSON string
    correct_answer = Column(String, nullable=False)
    question_type = Column(Enum(QuestionTypeEnum), nullable=False)
    confidence = Column(Integer, nullable=True)  # You could use Float if more precision is needed
    is_correct = Column(Boolean, default=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("UserAnswer", back_populates="question", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="question", cascade="all, delete-orphan")
