from enum import Enum
from typing import Literal


class DifficultyEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionTypeEnum(str, Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    IMAGE = "image"


# Type alias for quiz types - use this instead of redefining in multiple files
QuizType = Literal["MCQ", "TF", "IMAGE"]


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class GradingStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"


class HealthStatusEnum(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
