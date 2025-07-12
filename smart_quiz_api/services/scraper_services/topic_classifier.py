
## topic_classifier.py
from smart_quiz_api.services.openai_service import safe_openai_chat
import logging

logger = logging.getLogger(__name__)

def classify_topic(text: str) -> str:
    """Classify the topic of given text using AI."""
    try:
        if not text or len(text.strip()) < 50:
            return "General Knowledge"
            
        sample_text = text[:500]
        prompt = f"Classify this text into a single topic (e.g. History, Science, Technology, etc). Return only the topic name:\n\n{sample_text}"
        response = safe_openai_chat(prompt, max_tokens=50, temperature=0.3)
        topic = response.strip()
        
        # Validate topic response
        if topic and len(topic) <= 50 and not topic.lower().startswith(('i', 'the', 'this', 'here')):
            return topic
        else:
            return "General Knowledge"
            
    except Exception as e:
        logger.error(f"Topic classification failed: {str(e)}")
        return "General Knowledge"

