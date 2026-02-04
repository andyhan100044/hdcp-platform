import time
from typing import Callable, Dict, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
import os

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, default_limit: int = 100, window_size: int = 60):
        super().__init__(app)
        self.default_limit = default_limit
        self.window_size = window_size
        self.redis_client = None

    async def setup_redis(self):
        if self.redis_client is None:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url)

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Check for API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"

        # Fall back to client IP
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return f"ip:{client_ip}"

    async def _check_rate_limit(self, client_id: str, limit: int, window: int) -> Tuple[bool, int]:
        """Check if request is within rate limit. Returns (allowed, remaining)"""
        try:
            await self.setup_redis()

            key = f"hdcp:ratelimit:{client_id}"
            now = time.time()
            window_start = now - window

            # Use pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, window)
            results = await pipe.execute()

            current_requests = results[1]
            remaining = max(0, limit - current_requests)

            return current_requests < limit, remaining
        except Exception as e:
            print(f"Rate limit check error: {e}")
            return True, 999

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_id = self._get_client_id(request)

        # Get rate limit from custom header or use default
        rate_limit_header = request.headers.get("X-RateLimit-Limit", "")
        try:
            rate_limit = int(rate_limit_header) if rate_limit_header else self.default_limit
        except ValueError:
            rate_limit = self.default_limit

        allowed, remaining = await self._check_rate_limit(client_id, rate_limit, self.window_size)

        if not allowed:
            return Response(
                content='{"error": "Rate limit exceeded", "retry_after": ' + str(self.window_size) + '}',
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "X-RateLimit-Limit": str(rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + self.window_size),
                    "Retry-After": str(self.window_size)
                }
            )

        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_size)

        return response

class RateLimitConfig:
    def __init__(self):
        self.limits = {
            "default": {"requests": 100, "window": 60},
            "auth": {"requests": 10, "window": 60},
            "search": {"requests": 50, "window": 60},
            "api": {"requests": 1000, "window": 3600},
        }

    def get_limit(self, endpoint: str) -> Tuple[int, int]:
        """Get rate limit for endpoint. Returns (requests, window_seconds)"""
        for pattern, limit in self.limits.items():
            if pattern in endpoint:
                return limit["requests"], limit["window"]

        return self.limits["default"]["requests"], self.limits["default"]["window"]

rate_limit_config = RateLimitConfig()
