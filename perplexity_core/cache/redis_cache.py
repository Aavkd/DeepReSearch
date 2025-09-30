import redis
import json
from typing import Optional, Any
from ..config import settings


class Cache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get a value from the cache.
        """
        try:
            return self.redis_client.get(f"q:{key}")
        except Exception:
            return None
    
    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """
        Set a value in the cache with TTL.
        """
        try:
            self.redis_client.setex(f"q:{key}", ttl, value)
            return True
        except Exception:
            return False
    
    async def get_url_content(self, url_key: str) -> Optional[dict]:
        """
        Get cached URL content.
        """
        try:
            data = self.redis_client.hgetall(f"u:{url_key}")
            return data if data else None
        except Exception:
            return None
    
    async def set_url_content(self, url_key: str, content: dict, ttl: int = 604800) -> bool:  # 7 days default
        """
        Set cached URL content.
        """
        try:
            self.redis_client.hset(f"u:{url_key}", mapping=content)
            self.redis_client.expire(f"u:{url_key}", ttl)
            return True
        except Exception:
            return False