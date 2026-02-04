"""
Performance Optimization
Database query optimization and caching
"""
import time
import functools
from typing import Any, Callable, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis


class QueryOptimizer:
    """Database query optimizer"""

    @staticmethod
    async def optimize_stock_summary_query(
        db: AsyncSession,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Optimized query to get stock summary with a single database round trip
        Instead of multiple queries, we use a single query with aggregations
        """
        from app.models.stock import StockPrice
        from sqlalchemy import select, func, desc, and_
        from datetime import datetime, timedelta
        from decimal import Decimal

        # Single query with all aggregations
        query = select(
            # Latest price
            StockPrice.price.label("current_price"),
            StockPrice.price_change.label("price_change"),
            StockPrice.price_change_percent.label("price_change_percent"),
            StockPrice.volume.label("volume"),
            StockPrice.timestamp.label("last_updated"),

            # 30-day statistics
            func.avg(StockPrice.price).label("avg_price_30d"),
            func.min(StockPrice.price).label("min_price_30d"),
            func.max(StockPrice.price).label("max_price_30d"),
            func.sum(StockPrice.volume).label("total_volume_30d"),

            # 52-week statistics
            func.min(StockPrice.price).label("low_52w"),
            func.max(StockPrice.price).label("high_52w"),
        ).where(
            and_(
                StockPrice.symbol == symbol,
                StockPrice.timestamp >= datetime.utcnow() - timedelta(days=365)
            )
        ).group_by(
            StockPrice.price,
            StockPrice.price_change,
            StockPrice.price_change_percent,
            StockPrice.volume,
            StockPrice.timestamp
        ).order_by(
            desc(StockPrice.timestamp)
        ).limit(1)

        result = await db.execute(query)
        row = result.first()

        if not row:
            return None

        return {
            "symbol": symbol,
            "current_price": float(row.current_price or 0),
            "price_change": float(row.price_change or 0),
            "price_change_percent": float(row.price_change_percent or 0),
            "volume": row.volume or 0,
            "avg_price_30d": float(row.avg_price_30d or 0),
            "min_price_30d": float(row.min_price_30d or 0),
            "max_price_30d": float(row.max_price_30d or 0),
            "total_volume_30d": row.total_volume_30d or 0,
            "high_52w": float(row.high_52w or 0),
            "low_52w": float(row.low_52w or 0),
            "last_updated": row.last_updated
        }


class CacheManager:
    """Redis-based cache manager"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host="redis",
                port=6379,
                db=0,
                decode_responses=True
            )
            await self.redis_client.ping()
        except Exception:
            # Redis not available, cache will be disabled
            self.redis_client = None

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None

        try:
            import json
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 300  # 5 minutes default
    ) -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False

        try:
            import json
            await self.redis_client.setex(key, expire, json.dumps(value))
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception:
            return False

    async def clear_pattern(self, pattern: str) -> bool:
        """Clear all keys matching pattern"""
        if not self.redis_client:
            return False

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
            return True
        except Exception:
            return False


# Global cache instance
cache_manager = CacheManager()


def cached(
    key_prefix: str,
    expire: int = 300,
    key_func: Optional[Callable] = None
):
    """
    Cache decorator for async functions

    Usage:
        @cached("stocks", expire=60)
        async def get_stock_data(symbol: str):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = f"{key_prefix}:{key_func(*args, **kwargs)}"
            else:
                # Simple key generation
                key_parts = [key_prefix]
                key_parts.extend([str(arg) for arg in args])
                if kwargs:
                    sorted_kwargs = sorted(kwargs.items())
                    key_parts.extend([f"{k}={v}" for k, v in sorted_kwargs])
                cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache the result
            await cache_manager.set(cache_key, result, expire)

            return result

        return wrapper
    return decorator


class PerformanceMonitor:
    """Monitor and measure query performance"""

    def __init__(self):
        self.metrics: Dict[str, list] = {}

    def record_query(self, query_name: str, duration: float, success: bool = True):
        """Record query performance metrics"""
        if query_name not in self.metrics:
            self.metrics[query_name] = []

        self.metrics[query_name].append({
            "duration": duration,
            "success": success,
            "timestamp": time.time()
        })

    def get_query_stats(self, query_name: str) -> Optional[Dict[str, float]]:
        """Get performance statistics for a query"""
        if query_name not in self.metrics or not self.metrics[query_name]:
            return None

        metrics = self.metrics[query_name]
        durations = [m["duration"] for m in metrics if m["success"]]

        if not durations:
            return None

        return {
            "count": len(durations),
            "avg": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
            "total": sum(durations)
        }

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all queries"""
        return {
            name: stats for name, stats in [
                (name, self.get_query_stats(name))
                for name in self.metrics
            ]
            if stats is not None
        }


# Global performance monitor
performance_monitor = PerformanceMonitor()


def benchmark_query(query_name: str):
    """
    Decorator to benchmark database queries

    Usage:
        @benchmark_query("get_stock_price")
        async def get_stock_price(symbol: str):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                performance_monitor.record_query(query_name, duration, True)
                return result
            except Exception as e:
                duration = time.time() - start
                performance_monitor.record_query(query_name, duration, False)
                raise e

        return wrapper
    return decorator


# Initialize cache on startup
async def init_cache():
    """Initialize cache manager"""
    await cache_manager.connect()


async def close_cache():
    """Close cache manager"""
    await cache_manager.disconnect()
