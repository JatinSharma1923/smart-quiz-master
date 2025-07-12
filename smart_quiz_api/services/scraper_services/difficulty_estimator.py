
## difficulty_estimator.py
import logging
from typing import Literal

logger = logging.getLogger(__name__)

DifficultyLevel = Literal["easy", "medium", "hard"]

# Try to import textstat, fallback to simple estimation if not available
try:
    from textstat import flesch_kincaid_grade  # type: ignore
    _has_textstat = True
except ImportError:
    _has_textstat = False
    logger.warning("textstat library not available, using simple difficulty estimation")

def estimate_difficulty(text: str) -> DifficultyLevel:
    """Estimate the difficulty level of text using Flesch-Kincaid grade level."""
    try:
        if not text or len(text.strip()) < 50:
            return "medium"
            
        word_count = len(text.split())
        if word_count < 100:
            return "easy"

        if _has_textstat:
            grade = flesch_kincaid_grade(text)  # type: ignore
            if grade < 6:
                return "easy"
            elif grade < 10:
                return "medium"
            else:
                return "hard"
        else:
            # Simple fallback estimation based on word length and sentence complexity
            avg_word_length = sum(len(word) for word in text.split()) / word_count
            sentence_count = text.count('.') + text.count('!') + text.count('?')
            avg_sentence_length = word_count / max(sentence_count, 1)
            
            if avg_word_length > 6 or avg_sentence_length > 20:
                return "hard"
            elif avg_word_length > 5 or avg_sentence_length > 15:
                return "medium"
            else:
                return "easy"
                
    except Exception as e:
        logger.warning(f"Difficulty estimation failed: {str(e)}")
        return "medium"
