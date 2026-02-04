import json
import hashlib
from typing import Callable, Optional, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
import os

class CacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, cache_ttl: int = 300, exclude_paths: list = None):
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.redis_client = None
        self.exclude_paths = exclude_paths or []

    async def setup_redis(self):
        if self.redis_client is None:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url)

    def _get_cache_key(self, request: Request) -> str:
        """Generate cache key from request method and path"""
        key = f"{request.method}:{request.url.path}"
        if request.query_params:
            key += f"?{hashlib.md5(str(request.query_params).encode()).hexdigest()}"
        return f"hdcp:cache:{key}"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip caching for excluded paths
        if any(path in request.url.path for path in self.exclude_paths):
            return await call_next(request)

        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        await self.setup_redis()

        # Generate cache key
        cache_key = self._get_cache_key(request)

        # Try to get from cache
        try:
            cached_response = await self.redis_client.get(cache_key)
            if cached_response:
                return Response(
                    content=cached_response,
                    status_code=200,
                    headers={"X-Cache": "HIT"}
                )
        except Exception as e:
            print(f"Cache read error: {e}")

        # If not in cache, process request
        response = await call_next(request)

        # Only cache successful responses
        if response.status_code == 200:
            try:
                await self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    response.body
                )
                response.headers["X-Cache"] = "MISS"
            except Exception as e:
                print(f"Cache write error: {e}")

        return response

class CacheManager:
    def __init__(self):
        self.redis_client = None

    async def setup(self):
        if self.redis_client is None:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url)

    async def get(self, key: str) -> Optional[Any]:
        await self.setup()
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        await self.setup()
        try:
            await self.redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        await self.setup()
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> bool:
        await self.setup()
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return False

cache_manager = CacheManager()
