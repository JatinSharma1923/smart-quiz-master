import logging
import hashlib
from typing import Optional, Any

# === Logger ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# === Redis Service Setup ===
from smart_quiz_api.services.redis_service import redis_service

# === Cache Key Generator ===
def get_cache_key(prompt: str) -> str:
    """Return a SHA256-based key for caching AI prompt responses."""
    return f"quiz_cache:{hashlib.sha256(prompt.encode()).hexdigest()}"

# === Cache Getter ===
def get_cached_response(prompt: str) -> Optional[str]:
    """Get response from Redis if cached."""
    key = get_cache_key(prompt)
    try:
        result = redis_service.get(key)
        if result:
            logger.info(f"[Cache Hit] {key}")
            return result
    except Exception as e:
        logger.warning(f"[Cache Get Error] {e}")

    return None

# === Cache Setter ===
def set_cached_response(prompt: str, response: str, ttl: int = 3600):
    """Store AI response in Redis with TTL (default: 1 hour)."""
    key = get_cache_key(prompt)
    try:
        success = redis_service.setex(key, ttl, response)
        if success:
            logger.info(f"[Cache Store] {key} (TTL={ttl}s)")
    except Exception as e:
        logger.warning(f"[Cache Set Error] {e}")


# === Simple In-Memory Cache (Fallback) ===
_simple_cache: dict[str, str] = {}

def get_simple_cached_response(prompt: str) -> Optional[str]:
    """Get response from simple in-memory cache."""
    return _simple_cache.get(prompt)


def set_simple_cached_response(prompt: str, response: str):
    """Store response in simple in-memory cache."""
    _simple_cache[prompt] = response


def clear_simple_cache():
    """Clear the simple in-memory cache."""
    global _simple_cache
    _simple_cache.clear()
    logger.info("Simple cache cleared")


# === Cache Statistics ===
def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics."""
    try:
        return {
            "redis_connected": redis_service.is_connected(),
            "simple_cache_size": len(_simple_cache),
            "simple_cache_keys": list(_simple_cache.keys())[:10]  # First 10 keys
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {
            "redis_connected": False,
            "simple_cache_size": len(_simple_cache),
            "simple_cache_keys": list(_simple_cache.keys())[:10]
        }
