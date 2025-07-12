# cache.py
import hashlib
import json
from typing import Any, Dict, Optional
import logging

from smart_quiz_api.services.redis_service import redis_service

logger = logging.getLogger(__name__)

CACHE_TTL = 3600

def cache_key_url(url: str, quiz_type: str) -> str:
    combined = f"{quiz_type}:{url}"
    return f"url_quiz_cache:{hashlib.sha256(combined.encode('utf-8')).hexdigest()}"

def get_cached_quiz(url: str, quiz_type: str) -> Optional[Dict[str, Any]]:
    key = cache_key_url(url, quiz_type)
    try:
        # Check if Redis is available
        if not redis_service or not redis_service.is_connected():
            logger.warning("Redis not available for cache retrieval")
            return None
            
        result = redis_service.get(key)
        if result:
            return json.loads(result)
        return None
    except Exception as e:
        logger.warning(f"Redis cache error: {e}")
        return None

def set_cached_quiz(url: str, quiz_type: str, quiz_data: Dict[str, Any], ttl: int = CACHE_TTL) -> None:
    key = cache_key_url(url, quiz_type)
    try:
        # Check if Redis is available
        if not redis_service or not redis_service.is_connected():
            logger.warning("Redis not available for cache storage")
            return
            
        redis_service.setex(key, ttl, json.dumps(quiz_data))
    except Exception as e:
        logger.warning(f"Redis cache write failed: {e}")
