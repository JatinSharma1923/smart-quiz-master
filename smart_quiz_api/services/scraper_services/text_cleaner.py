

## text_cleaner.py
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

# Try to import readability, fallback to BeautifulSoup if not available
try:
    from readability import Document  # type: ignore
    _has_readability = True
except ImportError:
    _has_readability = False
    logger.warning("readability library not available, using BeautifulSoup fallback")

def extract_clean_text(html: str) -> str:
    """Extract clean text from HTML using readability or BeautifulSoup fallback."""
    if not html or not html.strip():
        raise ValueError("Empty HTML content")

    # Try readability first if available
    if _has_readability:
        try:
            doc = Document(html)  # type: ignore
            summary_html = doc.summary()  # type: ignore
            soup = BeautifulSoup(summary_html, "html.parser")  # type: ignore
            clean_text = soup.get_text(separator=" ", strip=True)

            if len(clean_text.split()) >= 100:
                return clean_text
            else:
                logger.warning("Readability produced insufficient content, using fallback")
        except Exception as e:
            logger.warning(f"Readability failed, using fallback: {str(e)}")

    # Fallback to BeautifulSoup
    try:
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.decompose()
            
        clean_text = soup.get_text(separator=" ", strip=True)

        if len(clean_text.split()) < 50:
            raise ValueError("Insufficient content extracted")

        return clean_text
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise

