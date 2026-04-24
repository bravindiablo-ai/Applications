"""
Redis caching service for improved performance and scalability.
"""
import json
from redis import asyncio as redis
from typing import Any, Optional, Union
from app.core.config import get_settings

class CacheService:
    """Redis caching service."""

    def __init__(self):
        """Initialize Redis connection."""
        self.settings = get_settings()
        self.redis = redis.from_url(self.settings.REDIS_URL)

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except (json.JSONDecodeError, Exception):
            return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set a value in cache with expiration (default 1 hour)."""
        try:
            await self.redis.setex(
                key,
                expire,
                json.dumps(value)
            )
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        try:
            await self.redis.delete(key)
            return True
        except Exception:
            return False

    async def get_trending(self, category: str = "all") -> list:
        """Get trending items from cache."""
        key = f"trending:{category}"
        return await self.get(key) or []

    async def cache_trending(self, items: list, category: str = "all", expire: int = 900) -> bool:
        """Cache trending items (default 15 minutes)."""
        key = f"trending:{category}"
        return await self.set(key, items, expire)

    async def get_personalized(self, user_id: str) -> list:
        """Get personalized recommendations from cache."""
        key = f"personalized:{user_id}"
        return await self.get(key) or []

    async def cache_personalized(self, user_id: str, items: list, expire: int = 3600) -> bool:
        """Cache personalized recommendations (default 1 hour)."""
        key = f"personalized:{user_id}"
        return await self.set(key, items, expire)

    async def get_token(self, token: str) -> Optional[dict]:
        """Get session token data from cache."""
        key = f"token:{token}"
        return await self.get(key)

    async def cache_token(self, token: str, data: dict, expire: int = 86400) -> bool:
        """Cache session token data (default 24 hours)."""
        key = f"token:{token}"
        return await self.set(key, data, expire)

    async def invalidate_token(self, token: str) -> bool:
        """Invalidate a session token."""
        key = f"token:{token}"
        return await self.delete(key)