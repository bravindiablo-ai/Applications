import os
try:
    import redis
except Exception:
    redis = None

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


class _InMemoryRedis:
    """Minimal in-memory redis-like client for dev/tests."""
    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def setex(self, key, ttl, value):
        # ignore ttl for in-memory
        self._store[key] = value

    def set(self, key, value):
        self._store[key] = value

    def from_url(self, url, decode_responses=True):
        return self


_FALLBACK = _InMemoryRedis()


def get_redis_client():
    """Return a redis client if available; otherwise an in-memory fallback.

    This allows dev verification without a running redis server or installed package.
    """
    if redis is None:
        return _FALLBACK
    try:
        return redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        return _FALLBACK
