# smart_quiz_api/schemas.py

from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import List, Optional
from datetime import datetime
from smart_quiz_api.models.enum import DifficultyEnum, QuestionTypeEnum


### === User ===
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str  # This will map to username in the model
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str = Field(..., alias="username")  # Map username from model to full_name in API
    total_quizzes_taken: int = 0
    average_score: float = 0.0
    streak: int = 0
    is_deleted: bool = False
    firebase_uid: Optional[str] = None
    profile_picture: Optional[str] = None
    is_admin: bool = False
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True  # Allow population by field name
    )


### === Answer ===
class AnswerCreate(BaseModel):
    text: str
    is_correct: Optional[bool] = False

class AnswerOut(BaseModel):
    id: int
    text: str
    is_correct: bool
    model_config = ConfigDict(from_attributes=True)


### === Question ===
class QuestionCreate(BaseModel):
    text: str
    correct_answer: str
    answers: List[AnswerCreate]

class QuestionOut(BaseModel):
    id: int
    text: str = Field(..., alias="question_text")  # Map question_text from model to text in API
    correct_answer: str
    answers: List[AnswerOut]
    question_type: Optional[str] = None
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True  # Allow population by field name
    )


### === Quiz ===
class QuizCreate(BaseModel):
    title: str
    topic: str = Field(..., description="Quiz category/topic")  # This will map to category in the model
    difficulty: str = Field(
        ..., 
        description="Quiz difficulty level", 
        examples=["easy", "medium", "hard"]
    )
    quiz_type: str = Field(
        ..., 
        description="Quiz question type", 
        examples=["mcq", "true_false", "image"]
    )
    questions: List[QuestionCreate]
    
    # Validate enum values
    @property
    def difficulty_enum(self) -> DifficultyEnum:
        try:
            return DifficultyEnum(self.difficulty.lower())
        except ValueError:
            raise ValueError(f"Invalid difficulty: {self.difficulty}. Must be one of: {[e.value for e in DifficultyEnum]}")
    
    @property
    def question_type_enum(self) -> QuestionTypeEnum:
        try:
            return QuestionTypeEnum(self.quiz_type.lower())
        except ValueError:
            raise ValueError(f"Invalid quiz_type: {self.quiz_type}. Must be one of: {[e.value for e in QuestionTypeEnum]}")
            
    # Additional validation
    def validate_questions(self) -> bool:
        """Validate that questions match the quiz type"""
        if not self.questions:
            raise ValueError("Quiz must have at least one question")
        return True

class QuizOut(BaseModel):
    id: int
    title: str
    topic: str = Field(..., alias="category")  # Map category from model to topic in API
    difficulty: str
    quiz_type: str  # This will need to be populated from the questions
    created_at: datetime
    questions: List[QuestionOut]
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Allow population by field name
        arbitrary_types_allowed=True  # This is needed for custom handling of quiz_type
    )


### === Badge ===
class BadgeOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    model_config = ConfigDict(from_attributes=True)


### === Feedback ===
class FeedbackCreate(BaseModel):
    message: str
    rating: Optional[int] = 5

class FeedbackOut(BaseModel):
    id: int
    message: str
    rating: Optional[int]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


### === API Key ===
class APIKeyOut(BaseModel):
    key_id: str
    user_id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


### === Generic Log ===
class LogOut(BaseModel):
    id: int
    event_type: str
    detail: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
# === New Additions to schema.py ===

class UserAnswerOut(BaseModel):
    id: int
    question_id: int
    selected_answer: str
    is_correct: bool
    model_config = ConfigDict(from_attributes=True)

class SessionLogOut(BaseModel):
    id: int
    login_time: datetime
    logout_time: Optional[datetime]
    ip_address: str
    device_info: str
    model_config = ConfigDict(from_attributes=True)

class WebSocketSessionOut(BaseModel):
    id: int
    connection_time: datetime
    disconnect_time: Optional[datetime]
    client_ip: str
    model_config = ConfigDict(from_attributes=True)

class GradingTaskOut(BaseModel):
    id: int
    quiz_id: int
    user_id: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class PromptTemplateOut(BaseModel):
    id: int
    name: str
    context: str
    template_text: str
    created_by: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PromptCacheOut(BaseModel):
    id: int
    prompt_hash: str
    response_text: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ErrorLogOut(BaseModel):
    id: int
    error_type: str
    message: str
    stack_trace: str
    occurred_at: datetime
    model_config = ConfigDict(from_attributes=True)

class HealthCheckLogOut(BaseModel):
    id: int
    service: str
    status: str
    checked_at: datetime
    response_time_ms: float
    model_config = ConfigDict(from_attributes=True)

# === Explicit API Response Models for OpenAPI and Validation ===

class CacheClearResponse(BaseModel):
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "Cache cleared successfully."}
        }
    )

class RedisStatsResponse(BaseModel):
    connected_clients: int
    memory_usage_mb: float
    uptime_seconds: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "connected_clients": 12,
                "memory_usage_mb": 42.5,
                "uptime_seconds": 86400
            }
        }
    )

class OpenAIStatusResponse(BaseModel):
    model: str
    status: str
    latency_ms: float
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "model": "gpt-3.5-turbo",
                "status": "healthy",
                "latency_ms": 123.4
            }
        }
    )

class UserStatsResponse(BaseModel):
    total_quizzes: int
    total_answers: int
    correct_answers: int
    accuracy: float
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_quizzes": 10,
                "total_answers": 50,
                "correct_answers": 40,
                "accuracy": 0.8
            }
        }
    )

class HealthCheckResponse(BaseModel):
    database: str
    redis: str
    openai: Optional[str] = None
    firebase: Optional[str] = None
    uptime: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "database": "healthy",
                "redis": "healthy",
                "openai": "healthy",
                "firebase": "healthy",
                "uptime": "1 day, 2:34:56"
            }
        }
    )

class DetailResponse(BaseModel):
    detail: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"detail": "Operation successful."}
        }
    )

