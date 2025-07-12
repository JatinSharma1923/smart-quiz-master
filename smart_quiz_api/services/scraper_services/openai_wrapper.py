
## openai_wrapper.py
# Use the main OpenAI service instead of duplicating functionality
from smart_quiz_api.services.openai_service import safe_openai_chat
from dotenv import load_dotenv
import logging
from typing import Optional
from smart_quiz_api.constants import DEFAULT_MODEL

logger = logging.getLogger(__name__)

load_dotenv()

# Get model from settings or use default
try:
    from smart_quiz_api.config import settings
    runtime_model = settings.scraper_model or DEFAULT_MODEL
except Exception as e:
    logger.warning(f"Could not load settings, using default model: {e}")
    runtime_model = DEFAULT_MODEL

def call_openai(prompt: str, model: Optional[str] = None) -> str:
    """Wrapper to use the main OpenAI service with retry logic built-in."""
    # Use provided model, runtime model from settings, or DEFAULT_MODEL as fallback
    model_to_use = model or runtime_model
    return safe_openai_chat(prompt, model=model_to_use, max_tokens=700, temperature=0.7)
