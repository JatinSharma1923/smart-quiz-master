
## quiz_generator.py
from datetime import datetime, timezone
from typing import Dict, Any
from .cache import get_cached_quiz, set_cached_quiz
from .content_fetcher import fetch_article_html
from .text_cleaner import extract_clean_text
from .topic_classifier import classify_topic
from .difficulty_estimator import estimate_difficulty
from .openai_wrapper import call_openai
import logging
from smart_quiz_api.constants import DEFAULT_MODEL
from smart_quiz_api.models.enum import QuizType

logger = logging.getLogger(__name__)

MAX_SNIPPET = 1600
MIN_SNIPPET = 1400
VALID_QUIZ_TYPES = ["MCQ", "TF", "IMAGE"]


def generate_quiz_from_url(
    url: str,
    quiz_type: QuizType = "MCQ", 
    model: str = DEFAULT_MODEL,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Generate a quiz from a URL by scraping content and using AI.
    
    Args:
        url: The URL to scrape content from
        quiz_type: Type of quiz to generate (MCQ, TF, IMAGE)
        model: OpenAI model to use for generation
        use_cache: Whether to use Redis caching
        
    Returns:
        Dictionary containing quiz data and metadata
        
    Raises:
        ValueError: If quiz_type is invalid or content extraction fails
    """
    if quiz_type not in VALID_QUIZ_TYPES:
        raise ValueError(f"Invalid quiz type: {quiz_type}. Must be one of {VALID_QUIZ_TYPES}")

    # Check cache first
    if use_cache:
        try:
            cached = get_cached_quiz(url, quiz_type)
            if cached:
                logger.info(f"Returning cached quiz for {url} ({quiz_type})")
                return cached
        except Exception as e:
            logger.warning(f"Cache retrieval failed, continuing without cache: {e}")

    try:
        # Fetch and process content
        html = fetch_article_html(url)
        clean_text = extract_clean_text(html)
        
        if len(clean_text.split()) < 100:
            raise ValueError("Insufficient content extracted from URL")
            
        topic = classify_topic(clean_text)
        difficulty = estimate_difficulty(clean_text)

        # Create content snippet
        snippet = clean_text[:MAX_SNIPPET]
        for end in range(min(len(clean_text), MAX_SNIPPET), MIN_SNIPPET, -1):
            if clean_text[end:end+1] in ".!?":
                snippet = clean_text[:end+1]
                break

        # Generate quiz prompt
        prompt = f"""Generate a {quiz_type} quiz based on the following content.

Topic: {topic}
Difficulty: {difficulty}

Content:
{snippet}

Instructions:
- For MCQ: Create 5 multiple choice questions with 4 options each
- For TF: Create 10 true/false questions  
- For IMAGE: Create 5 questions that would work well with images/diagrams

Format the output as a structured quiz with clear questions and answers."""

        try:
            quiz = call_openai(prompt, model=model)
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            # Provide a fallback response
            quiz = f"Failed to generate quiz. Error: {str(e)}"
        
        result = {
            "topic": topic,
            "difficulty": difficulty,
            "quiz_type": quiz_type,
            "source_url": url,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "content_excerpt": snippet,
            "quiz": quiz
        }

        # Cache the result
        if use_cache:
            try:
                set_cached_quiz(url, quiz_type, result)
            except Exception as e:
                logger.warning(f"Failed to cache quiz: {e}")
            
        logger.info(f"Generated {quiz_type} quiz for {url} (topic: {topic}, difficulty: {difficulty})")
        return result
        
    except Exception as e:
        logger.error(f"Failed to generate quiz from {url}: {str(e)}")
        raise
