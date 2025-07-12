import logging
import re
from typing import List, Dict, Any, Optional, cast
import json

from smart_quiz_api.services.openai_service.ai_client import(
    get_valid_model,
    fallback_response,
    trim_prompt_to_fit,
    call_openai
)
from smart_quiz_api.services.openai_service.cache import get_cached_response, set_cached_response
from smart_quiz_api.services.redis_service import redis_service
from smart_quiz_api.constants import DEFAULT_MODEL

logger = logging.getLogger(__name__)


# === OpenAI Safe Wrapper ===
def safe_openai_chat(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 700, temperature: float = 0.7) -> str:
    model = get_valid_model(model)
    prompt = trim_prompt_to_fit(prompt, 4000, model)

    try:
        cached = get_cached_response(prompt)
        if cached:
            return cached

        response = call_openai(prompt, model=model, max_tokens=max_tokens, temperature=temperature)
        set_cached_response(prompt, response)
        return response
    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        return fallback_response(prompt)

def parse_ai_quiz_response(ai_response: Dict[str, Any] | str, quiz_type: str) -> List[Dict[str, Any]]:
    """
    Parses the AI-generated quiz response into a standardized format.

    Args:
        ai_response (Union[Dict[str, Any], str]): Raw OpenAI response containing quiz data or string content.
        quiz_type (str): The type of quiz (e.g., "mcq", "true_false").

    Returns:
        List[Dict[str, Any]]: Structured quiz questions.

    Raises:
        ValueError: If the content is malformed or missing.
    """
    try:
        if not ai_response:
            raise ValueError("Empty response from OpenAI")

        # Handle string responses directly (from safe_openai_chat)
        if isinstance(ai_response, str):
            content = ai_response.strip()
        else:
            # Handle dictionary responses (from direct OpenAI API calls)
            content = (
                ai_response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )

        if not content:
            raise ValueError("Missing content in OpenAI response")

        # Parse JSON content
        try:
            questions_raw = json.loads(content)
        except json.JSONDecodeError:
            # Try to handle non-JSON formatted responses
            logger.warning("Response is not valid JSON, attempting to parse as text")
            # Simple fallback for text responses - create a single question
            return [{"question": "Generated quiz could not be parsed properly", 
                    "options": ["Option A", "Option B", "Option C", "Option D"], 
                    "answer": "Option A"}]

        if not isinstance(questions_raw, list):
            raise ValueError("Expected list of questions")

        # Enforce correct type
        questions: List[Dict[str, Any]] = cast(List[Dict[str, Any]], questions_raw)

        for q in questions:
            if "question" not in q or "options" not in q or "answer" not in q:
                raise ValueError("Malformed question format")

        logger.info(f"✅ Parsed {len(questions)} questions for quiz type: {quiz_type}")
        return questions

    except Exception as e:
        logger.error(f"❌ Failed to parse AI quiz response: {e}")
        raise ValueError(f"Error parsing AI response: {e}")

# === OTHER TASKS ===



# === Topic Classifier ===
def classify_topic(content: str) -> str:
    prompt = f"Classify the following content into a topic (e.g., Science, History, Tech, etc):\n\n{content[:1000]}"
    try:
        return safe_openai_chat(prompt)
    except Exception as e:
        logger.warning(f"Topic classification failed: {e}")
        return "General Knowledge"


# === Explanation Generator ===
def generate_explanation(quiz_text: str) -> str:
    prompt = f"Explain each correct answer in the following quiz in 1-2 beginner-friendly sentences:\n\n{quiz_text}"
    return safe_openai_chat(prompt)


# === Tag Generator ===
def generate_tags(question: str) -> List[str]:
    prompt = f"Give 3 relevant tags (comma-separated) for this question:\n{question}"
    try:
        response = safe_openai_chat(prompt)
        return [tag.strip() for tag in response.split(",") if tag.strip()]
    except Exception as e:
        logger.error(f"Tag generation failed: {e}")
        return []


# === Answer Grader ===
def grade_answer(user_answer: str, correct_option: str, explanation: Optional[str] = "") -> Dict[str, Any]:
    is_correct = user_answer.strip().upper() == correct_option.strip().upper()
    feedback_prompt = (
        f"The correct answer is {correct_option}. The user selected {user_answer}. "
        f"Is it correct? Justify with explanation."
    )
    try:
        feedback = safe_openai_chat(feedback_prompt)
    except Exception as e:
        logger.error(f"Grading feedback failed: {e}")
        feedback = "Feedback unavailable."

    return {
        "is_correct": is_correct,
        "feedback": feedback
    }


# === Confidence Estimator ===
def estimate_confidence(quiz_block: str) -> float:
    prompt = f"Rate the confidence in this quiz block on a scale from 0.0 to 1.0:\n{quiz_block}"
    try:
        response = safe_openai_chat(prompt)
        numbers = re.findall(r'\d+\.?\d*', response)
        if numbers:
            confidence = float(numbers[0])
            return min(max(confidence, 0.0), 1.0)
        return 0.8
    except Exception as e:
        logger.error(f"Confidence estimation failed: {e}")
        return 0.8


# === Health Check ===
def check_openai_health() -> Dict[str, Any]:
    health = {
        "redis": {"status": "unknown"},
        "openai": {"status": "unknown"},
        "overall": {"status": "unknown"}
    }

    # Redis health
    try:
        if redis_service.is_connected():
            health["redis"]["status"] = "healthy"
        else:
            health["redis"]["status"] = "unhealthy"
            health["redis"]["error"] = "Redis connection failed"
    except Exception as e:
        health["redis"]["status"] = "unhealthy"
        health["redis"]["error"] = str(e)

    # OpenAI health
    try:
        test_response = safe_openai_chat("Say 'OK'", max_tokens=10)
        if "OK" in test_response.upper():
            health["openai"]["status"] = "healthy"
        else:
            health["openai"]["status"] = "degraded"
    except Exception as e:
        health["openai"]["status"] = "unhealthy"
        health["openai"]["error"] = str(e)



    # Overall
    if health["redis"]["status"] == "healthy" and health["openai"]["status"] == "healthy":
        health["overall"]["status"] = "healthy"
    elif health["redis"]["status"] == "unhealthy" or health["openai"]["status"] == "unhealthy":
        health["overall"]["status"] = "unhealthy"
    else:
        health["overall"]["status"] = "degraded"

    return health
