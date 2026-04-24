import redis.asyncio as redis
import json
from typing import Any, Optional
from app.core.config import get_settings

settings = get_settings()

class CacheManager:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        return await self.redis_client.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            await self.redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            await self.redis_client.delete(key)
            return True
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return bool(await self.redis_client.exists(key))
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear cache keys matching pattern."""
        keys = await self.redis_client.keys(pattern)
        if keys:
            return await self.redis_client.delete(*keys)
        return 0

cache_manager = CacheManager()
