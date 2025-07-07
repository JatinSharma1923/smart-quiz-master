from .base import Base

# Import all models so they are registered with SQLAlchemy metadata
from .user import User
from .quiz import Quiz, QuizQuestion
from .answer import UserAnswer
from .badge import Badge, UserBadge
from .feedback import Feedback
from .log import (
    SessionLog,
    RequestLog,
    ErrorLog,
    APIKey,
    RateLimitLog,
    HealthCheckLog
)
from .background import (
    BackgroundTaskQueue,
    WebSocketSession,
    GradingTask
)
from .prompt import PromptTemplate, PromptCache

# Optionally: Enum imports for external access
from .enum import (
    DifficultyEnum,
    QuestionTypeEnum,
    TaskStatusEnum,
    GradingStatusEnum,
    HealthStatusEnum,
)
