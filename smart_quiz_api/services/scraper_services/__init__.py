# Re-export main interface and utilities for external usage
from .interface import scrape_and_generate_quiz
from .quiz_generator import generate_quiz_from_url
from .content_fetcher import fetch_article_html, is_valid_url
from .text_cleaner import extract_clean_text
from .topic_classifier import classify_topic
from .difficulty_estimator import estimate_difficulty
from .cache import get_cached_quiz, set_cached_quiz
from smart_quiz_api.models.enum import QuizType

__all__ = [
    "scrape_and_generate_quiz",
    "generate_quiz_from_url", 
    "QuizType",
    "fetch_article_html",
    "is_valid_url",
    "extract_clean_text",
    "classify_topic",
    "estimate_difficulty",
    "get_cached_quiz",
    "set_cached_quiz"
]

