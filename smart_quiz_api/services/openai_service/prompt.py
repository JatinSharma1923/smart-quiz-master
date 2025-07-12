import os
import logging
from functools import lru_cache

from smart_quiz_api.models.enum import QuizType
from smart_quiz_api.core.exceptions import PromptTemplateNotFound

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# === Valid Quiz Types ===
VALID_QUIZ_TYPES = {"MCQ", "TF", "IMAGE"}

# === Load Prompt Template from File ===
@lru_cache(maxsize=10)
def load_prompt_template(quiz_type: QuizType) -> str:
    """
    Load prompt template from templates directory.
    Expects template files at: smart_quiz_api/templates/{quiz_type}.txt
    """
    # Validate quiz type
    if quiz_type not in VALID_QUIZ_TYPES:
        raise ValueError(f"Invalid quiz type: {quiz_type}. Must be one of {VALID_QUIZ_TYPES}")
    
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate to templates directory
    templates_dir = os.path.join(current_dir, "..", "..", "templates")
    path = os.path.join(templates_dir, f"{quiz_type.lower()}.txt")
    
    if not os.path.exists(path):
        logger.error(f"❌ Prompt template not found at path: {path}")
        raise PromptTemplateNotFound(f"Template for quiz type '{quiz_type}' not found.")

    try:
        with open(path, "r", encoding="utf-8") as file:
            template = file.read()
            logger.info(f"✅ Loaded prompt template: {quiz_type}")
            return template
    except Exception:
        logger.exception(f"Unexpected error loading prompt template from {path}")
        raise

# === Render Prompt with Values ===
def render_prompt(topic: str, difficulty: str, quiz_type: QuizType) -> str:
    """
    Fill in topic and difficulty into the loaded prompt template.
    """
    try:
        template = load_prompt_template(quiz_type)
        rendered = template.replace("{topic}", topic).replace("{difficulty}", difficulty)
        logger.info(f"🧠 Rendered prompt for quiz_type={quiz_type}, topic={topic}, difficulty={difficulty}")
        return rendered
    except Exception:
        logger.exception(f"Failed to render prompt for type '{quiz_type}' with topic '{topic}' and difficulty '{difficulty}'")
        raise
