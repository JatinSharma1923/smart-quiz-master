# smart_quiz_api/utils/text_utils.py

import re
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"

def load_template(template_name: str) -> str:
    """Load a template file from the templates directory."""
    path = TEMPLATE_DIR / template_name
    if not path.exists():
        raise FileNotFoundError(f"Template '{template_name}' not found at {path}")
    return path.read_text(encoding="utf-8")

def render_template(template_name: str, context: Dict[str, str]) -> str:
    """Render a template with the given context variables."""
    template = load_template(template_name)
    for key, value in context.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template

def truncate_text(text: str, max_words: int = 1500) -> str:
    """Truncate text to a maximum number of words."""
    if not text:
        return ""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."

def clean_text_for_quiz(text: str) -> str:
    """Clean text for quiz generation by removing unwanted elements."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common HTML-like tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove special characters that might interfere with quiz generation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
    
    return text

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract important keywords from text for quiz generation."""
    if not text:
        return []
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can'
    }
    
    # Extract words and filter
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    keywords = [word for word in words if word not in stop_words]
    
    # Count frequency and return most common
    from collections import Counter
    word_counts = Counter(keywords)
    return [word for word, _ in word_counts.most_common(max_keywords)]

def generate_text_hash(text: str) -> str:
    """Generate a hash for text to use as cache key."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def split_text_into_chunks(text: str, max_chunk_size: int = 1000) -> List[str]:
    """Split text into chunks for processing."""
    if not text:
        return []
    
    words = text.split()
    chunks: List[str] = []
    current_chunk: List[str] = []
    current_size = 0
    
    for word in words:
        if current_size + len(word) + 1 > max_chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_size = len(word)
        else:
            current_chunk.append(word)
            current_size += len(word) + 1
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def validate_quiz_text(text: str, min_words: int = 50) -> Tuple[bool, str]:
    """Validate if text is suitable for quiz generation."""
    if not text or not text.strip():
        return False, "Text is empty"
    
    word_count = len(text.split())
    if word_count < min_words:
        return False, f"Text too short ({word_count} words, minimum {min_words})"
    
    # Check for repetitive content
    words = text.lower().split()
    unique_words = set(words)
    if len(unique_words) < word_count * 0.3:  # Less than 30% unique words
        return False, "Text appears to be too repetitive"
    
    return True, "Text is suitable for quiz generation"

def format_quiz_question(question: str, options: List[str], correct_answer: str) -> str:
    """Format a quiz question for display."""
    formatted = f"Question: {question}\n\n"
    for i, option in enumerate(options, 1):
        marker = "✓" if option == correct_answer else "○"
        formatted += f"{marker} {i}. {option}\n"
    return formatted

