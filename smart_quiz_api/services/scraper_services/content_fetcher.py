
## content_fetcher.py
import requests
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

def is_valid_url(url: str) -> bool:
    """Validate if the given string is a valid HTTP/HTTPS URL."""
    try:
        if not url:
            return False
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False

def fetch_article_html(url: str) -> str:
    """Fetch HTML content from a URL with proper error handling."""
    if not is_valid_url(url):
        raise ValueError(f"Invalid URL: {url}")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Check content size (10MB limit)
        if len(response.content) > 10 * 1024 * 1024:
            raise ValueError("Content too large (>10MB)")

        # Check if we got HTML content
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type and 'application/xhtml' not in content_type:
            logger.warning(f"Content type is not HTML: {content_type}")

        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for URL {url}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to fetch URL {url}: {str(e)}")
        raise
