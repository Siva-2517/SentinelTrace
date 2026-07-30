import json
from typing import Optional, Dict, Any
try:

    # pyrefly: ignore [missing-import]
    import redis.asyncio as aioredis
except ImportError:
    try:
        from redis import asyncio as aioredis  # type: ignore
    except ImportError:
        aioredis = None  # type: ignore

from app.config import settings
from app.core.logging_config import logger

_redis_client: Any = None


async def get_redis_client() -> Any:
    """Returns an async Redis client instance, or None if connection fails or package is missing."""
    global _redis_client
    if aioredis is None:
        return None
    if _redis_client is None:
        try:
            extra_args = {}
            if settings.REDIS_URL.startswith("rediss://"):
                extra_args["ssl_cert_reqs"] = None

            _redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=1.5,
                **extra_args
            )
            # Test ping
            await _redis_client.ping()
            logger.info("Connected to Redis successfully.", url=settings.REDIS_URL)
        except Exception as e:
            logger.warning("Redis connection failed. Running without Redis cache fallback.", error=str(e))
            _redis_client = None
    return _redis_client


async def cache_get_json(key: str) -> Optional[Dict[str, Any]]:
    """Get JSON object from Redis cache with error handling."""
    try:
        client = await get_redis_client()
        if not client:
            return None
        val = await client.get(key)
        return json.loads(val) if val else None
    except Exception as e:
        logger.debug("Redis GET error", key=key, error=str(e))
        return None


async def cache_set_json(key: str, data: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
    """Set JSON object in Redis cache with TTL and error handling."""
    try:
        client = await get_redis_client()
        if not client:
            return False
        await client.setex(key, ttl_seconds, json.dumps(data))
        return True
    except Exception as e:
        logger.debug("Redis SET error", key=key, error=str(e))
        return False


async def cache_delete(key: str) -> bool:
    """Delete a key from Redis cache."""
    try:
        client = await get_redis_client()
        if not client:
            return False
        await client.delete(key)
        return True
    except Exception as e:
        logger.debug("Redis DELETE error", key=key, error=str(e))
        return False
