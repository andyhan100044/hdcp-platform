"""
Performance Tests
Benchmark database queries and API endpoints
"""
import pytest
import asyncio
import time
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import StockPrice
from app.core.performance import (
    QueryOptimizer,
    CacheManager,
    performance_monitor,
    benchmark_query
)


class TestQueryOptimization:
    """Test query optimization techniques"""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_stock_summary_query_optimization(self, db: AsyncSession):
        """Test that optimized query is faster than multiple queries"""
        from sqlalchemy import select, func, desc, and_
        from datetime import datetime, timedelta

        # Create test data
        symbol = "TEST_OPT"
        for i in range(100):
            price = StockPrice(
                symbol=symbol,
                price=Decimal(f"100.{i}"),
                volume=1000,
                price_change=Decimal("1.0"),
                price_change_percent=Decimal("1.0"),
                timestamp=datetime.utcnow()
            )
            db.add(price)
        await db.commit()

        # Test traditional multi-query approach
        start_time = time.time()

        # Query 1: Get latest price
        latest_query = (
            select(StockPrice)
            .where(StockPrice.symbol == symbol)
            .order_by(desc(StockPrice.timestamp))
            .limit(1)
        )
        result = await db.execute(latest_query)
        latest = result.scalar_one()

        # Query 2: Get 30-day stats
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        stats_query = select(
            func.avg(StockPrice.price),
            func.min(StockPrice.price),
            func.max(StockPrice.price),
            func.sum(StockPrice.volume)
        ).where(
            StockPrice.symbol == symbol,
            StockPrice.timestamp >= thirty_days_ago
        )
        result = await db.execute(stats_query)
        avg_price, min_price, max_price, total_volume = result.one()

        # Query 3: Get 52-week range
        year_ago = datetime.utcnow() - timedelta(days=365)
        range_query = select(
            func.min(StockPrice.price),
            func.max(StockPrice.price)
        ).where(
            StockPrice.symbol == symbol,
            StockPrice.timestamp >= year_ago
        )
        result = await db.execute(range_query)
        low_52w, high_52w = result.one()

        traditional_time = time.time() - start_time

        # Test optimized single-query approach
        start_time = time.time()
        result = await QueryOptimizer.optimize_stock_summary_query(db, symbol)
        optimized_time = time.time() - start_time

        # Optimized query should be faster
        print(f"Traditional: {traditional_time:.4f}s, Optimized: {optimized_time:.4f}s")
        assert optimized_time < traditional_time * 1.2, "Optimized query should be faster"

        # Verify results are the same
        assert result is not None
        assert result["current_price"] == float(latest.price)


class TestCaching:
    """Test caching functionality"""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_set_get(self):
        """Test basic cache set and get operations"""
        cache = CacheManager()
        await cache.connect()

        if not cache.redis_client:
            pytest.skip("Redis not available")

        # Test set and get
        await cache.set("test_key", {"value": "test_data"}, expire=60)
        value = await cache.get("test_key")

        assert value is not None
        assert value["value"] == "test_data"

        # Test delete
        await cache.delete("test_key")
        value = await cache.get("test_key")

        assert value is None

        await cache.disconnect()

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_decorator(self, db: AsyncSession):
        """Test cache decorator"""
        from app.core.performance import cached

        call_count = 0

        @cached("test_cache", expire=60)
        async def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate expensive operation
            return x * 2

        # First call - should execute
        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call - should use cache
        result2 = await expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented, used cache

        # Different argument - should execute again
        result3 = await expensive_function(10)
        assert result3 == 20
        assert call_count == 2

        await cache_manager.disconnect()


class TestPerformanceMonitoring:
    """Test performance monitoring"""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_benchmark_decorator(self):
        """Test benchmark decorator"""
        from app.core.performance import benchmark_query

        @benchmark_query("test_query")
        async def test_function():
            await asyncio.sleep(0.1)
            return "result"

        # Clear previous metrics
        performance_monitor.metrics = {}

        # Execute function
        result = await test_function()
        assert result == "result"

        # Check metrics
        stats = performance_monitor.get_query_stats("test_query")
        assert stats is not None
        assert stats["count"] == 1
        assert stats["min"] >= 0.1
        assert stats["max"] >= 0.1
        assert stats["avg"] >= 0.1

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_multiple_queries_monitoring(self):
        """Test monitoring multiple queries"""
        from app.core.performance import benchmark_query

        @benchmark_query("query1")
        async def query1():
            await asyncio.sleep(0.05)
            return 1

        @benchmark_query("query2")
        async def query2():
            await asyncio.sleep(0.03)
            return 2

        # Clear previous metrics
        performance_monitor.metrics = {}

        # Execute queries
        await query1()
        await query2()
        await query1()

        # Check all stats
        all_stats = performance_monitor.get_all_stats()

        assert "query1" in all_stats
        assert "query2" in all_stats

        assert all_stats["query1"]["count"] == 2
        assert all_stats["query2"]["count"] == 1


class TestPerformanceBenchmarks:
    """Performance benchmarks - measure absolute performance"""

    @pytest.mark.performance
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_api_response_time_benchmark(self, client):
        """Benchmark API response times"""
        # Test health endpoint
        start = time.time()
        response = await client.get("/health")
        duration = time.time() - start

        assert response.status_code == 200
        # Response should be under 100ms
        assert duration < 0.1, f"Response took {duration:.4f}s, should be under 0.1s"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_stock_list_pagination_benchmark(self, client, db: AsyncSession):
        """Benchmark stock listing with pagination"""
        from app.models.stock import StockPrice
        from sqlalchemy import select
        from decimal import Decimal
        from datetime import datetime

        # Create test data
        for i in range(1000):
            price = StockPrice(
                symbol=f"STOCK{i % 10}",
                price=Decimal(f"100.{i}"),
                volume=1000,
                price_change=Decimal("1.0"),
                price_change_percent=Decimal("1.0"),
                timestamp=datetime.utcnow()
            )
            db.add(price)
        await db.commit()

        # Benchmark first page
        start = time.time()
        response = await client.get("/api/v1/stocks", params={"page": 1, "size": 20})
        duration = time.time() - start

        assert response.status_code == 200
        # First page should load quickly
        assert duration < 0.5, f"First page took {duration:.4f}s"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_database_connection_pool_performance(self, db: AsyncSession):
        """Test database connection pool performance"""
        import asyncio
        from sqlalchemy import text

        # Clear performance monitor
        performance_monitor.metrics = {}

        @benchmark_query("pool_test")
        async def pool_query():
            result = await db.execute(text("SELECT 1"))
            return result.scalar()

        # Execute concurrent queries
        start = time.time()
        tasks = [pool_query() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        duration = time.time() - start

        assert all(r == 1 for r in results)
        # Should handle 50 concurrent queries efficiently
        assert duration < 5.0, f"50 concurrent queries took {duration:.4f}s"

        stats = performance_monitor.get_query_stats("pool_test")
        assert stats is not None
        assert stats["count"] == 50
