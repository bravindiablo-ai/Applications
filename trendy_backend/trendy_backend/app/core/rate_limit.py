from typing import Optional
from app.core.cache import cache_manager
from app.core.config import get_settings

settings = get_settings()

class RateLimiter:
    def __init__(self):
        self.cache = cache_manager
    async def check_rate_limit(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request is within rate limit."""
        current = await self.cache.redis_client.incr(key)
        if current == 1:
            await self.cache.redis_client.expire(key, window)
        return current <= limit

    async def get_remaining_requests(self, key: str, limit: int) -> int:
        """Get remaining requests for rate limit."""
        current = int(await self.cache.redis_client.get(key) or 0)
        return max(0, limit - current)
