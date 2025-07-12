from typing import Literal
from .quiz_generator import generate_quiz_from_url
from smart_quiz_api.constants import DEFAULT_MODEL

# Define allowed quiz types
QuizType = Literal["MCQ", "TF", "IMAGE"]

def scrape_and_generate_quiz(
    url: str,
    quiz_type: QuizType = "MCQ",
    model: str = DEFAULT_MODEL,
    use_cache: bool = True
):
    """
    Main interface function to generate a quiz from a URL.
    - Can be used by FastAPI routes or CLI
    - Handles quiz_type and model forwarding

    Args:
        url (str): URL to scrape
        quiz_type (Literal): One of ["MCQ", "TF", "IMAGE"]
        model (str): OpenAI model
        use_cache (bool): Enable Redis caching

    Returns:
        dict: Quiz data object
    """
    # If you're planning to pass model/use_cache later, update generate_quiz_from_url
    return generate_quiz_from_url(url, quiz_type, model=model, use_cache=use_cache)
