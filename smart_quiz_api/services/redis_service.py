# smart_quiz_api/services/redis_service.py
# Redis Service Wrapper with Type Ignore for Redis Library Issues

import redis
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import logging
from smart_quiz_api.config import settings

logger = logging.getLogger(__name__)

load_dotenv()

class RedisService:
    """Redis service wrapper with type ignore for Redis library issues."""
    
    def __init__(self, url: Optional[str] = None):
        self.url = url or settings.redis_url
        self._client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish Redis connection with error handling."""
        try:
            self._client = redis.Redis.from_url(self.url, decode_responses=True)  # type: ignore
            # Test connection
            self._client.ping()  # type: ignore
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None
    
    @property
    def client(self) -> Optional[redis.Redis]:
        """Get Redis client with connection check."""
        if self._client is None:
            self._connect()
        return self._client
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        try:
            return self.client is not None and bool(self.client.ping())  # type: ignore
        except Exception:
            return False
    
    def flush_db(self) -> bool:
        """Clear all data from current database."""
        try:
            if self.client:
                self.client.flushdb()  # type: ignore
                logger.info("Redis database cleared successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to clear Redis database: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis server statistics."""
        try:
            if self.client:
                info = self.client.info()  # type: ignore
                if isinstance(info, dict):
                    return {
                        "connected": True,
                        "version": info.get("redis_version", "unknown"),  # type: ignore
                        "used_memory": info.get("used_memory_human", "unknown"),  # type: ignore
                        "connected_clients": info.get("connected_clients", 0),  # type: ignore
                        "total_commands_processed": info.get("total_commands_processed", 0)  # type: ignore
                    }
                return {"connected": True, "version": "unknown", "used_memory": "unknown", "connected_clients": 0, "total_commands_processed": 0}
            return {"connected": False, "error": "No Redis connection"}
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
            return {"connected": False, "error": str(e)}
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis with proper error handling."""
        try:
            if self.client:
                result = self.client.get(key)  # type: ignore
                if result is None:
                    return None
                if isinstance(result, bytes):
                    try:
                        return result.decode("utf-8")
                    except UnicodeDecodeError:
                        logger.warning(f"Could not decode bytes for key {key} as UTF-8, returning string representation")
                        return str(result)
                return str(result)
            return None
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None
    
    def setex(self, key: str, ttl: int, value: str) -> bool:
        """Set value in Redis with TTL and proper error handling."""
        try:
            if self.client:
                self.client.setex(key, ttl, value)  # type: ignore
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False

# Global Redis service instance
redis_service = RedisService() 