# 🚀 HDCP 性能优化指南

本文档说明HDCP模板中实施的性能优化技术。

---

## 📋 性能优化概览

HDCP模板实施了多层性能优化：

- ✅ 数据库连接池优化
- ✅ 查询优化 (消除N+1查询)
- ✅ Redis缓存层
- ✅ 性能监控和基准测试
- ✅ 异步I/O优化

---

## 🗄️ 数据库连接池优化

### 连接池配置

已在 `apps/api/app/database.py` 中配置了优化的连接池：

```python
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    settings.database_url,
    poolclass=QueuePool,  # 使用QueuePool而非NullPool
    pool_size=20,         # 基础连接数
    max_overflow=30,      # 最大溢出连接
    pool_timeout=30,       # 获取连接超时时间
    pool_recycle=3600,     # 连接回收时间(1小时)
    pool_pre_ping=True,    # 预验证连接
)
```

### 配置说明

| 参数 | 值 | 说明 |
|------|-----|-----|
| `pool_size` | 20 | 基础连接池大小 |
| `max_overflow` | 30 | 超出基础大小的额外连接 |
| `pool_timeout` | 30秒 | 等待连接超时 |
| `pool_recycle` | 3600秒 | 连接回收时间 |
| `pool_pre_ping` | True | 获取连接前验证 |

### 环境适配

```python
# 测试环境使用NullPool避免连接冲突
poolclass = NullPool if settings.environment == "testing" else QueuePool
```

---

## ⚡ 查询优化

### 问题：N+1查询

原始实现使用多个查询获取数据：

```python
# ❌ 低效：3个查询
latest = get_latest_price(symbol)        # 查询1
stats = get_30day_stats(symbol)          # 查询2
range_data = get_52week_range(symbol)     # 查询3
```

### 解决方案：单查询聚合

```python
# ✅ 高效：1个查询包含所有聚合
query = select(
    func.avg(StockPrice.price),
    func.min(StockPrice.price),
    func.max(StockPrice.price),
    func.sum(StockPrice.volume),
    # ... 更多聚合
).where(
    StockPrice.symbol == symbol,
    StockPrice.timestamp >= year_ago
).group_by(...)

result = await db.execute(query)
data = result.first()
```

### 使用QueryOptimizer

```python
from app.core.performance import QueryOptimizer

result = await QueryOptimizer.optimize_stock_summary_query(db, symbol)
```

---

## 💾 缓存系统

### Redis缓存

在 `apps/api/app/core/performance.py` 中实现了Redis缓存：

```python
from app.core.performance import cached

@cached("stocks", expire=60)
async def get_stock_data(symbol: str):
    # 从数据库获取数据
    data = await db.execute(select(StockPrice)...)
    return data
```

### 缓存键生成

自动生成缓存键：

```python
@cached("stock_summary", expire=60, key_func=lambda symbol: symbol.lower())
async def get_stock_summary(symbol: str):
    return data

# 缓存键: stock_summary:AAPL
```

### 手动缓存操作

```python
from app.core.performance import cache_manager

# 设置缓存
await cache_manager.set("key", value, expire=300)

# 获取缓存
value = await cache_manager.get("key")

# 删除缓存
await cache_manager.delete("key")

# 批量删除
await cache_manager.clear_pattern("stocks:*")
```

---

## 📊 性能监控

### 基准测试装饰器

使用 `@benchmark_query` 装饰器监控查询性能：

```python
from app.core.performance import benchmark_query

@benchmark_query("get_stock_price")
async def get_stock_price(symbol: str):
    result = await db.execute(query)
    return result
```

### 获取性能统计

```python
from app.core.performance import performance_monitor

# 获取单个查询统计
stats = performance_monitor.get_query_stats("get_stock_price")
print(f"查询次数: {stats['count']}")
print(f"平均耗时: {stats['avg']:.4f}s")
print(f"最快: {stats['min']:.4f}s")
print(f"最慢: {stats['max']:.4f}s")

# 获取所有查询统计
all_stats = performance_monitor.get_all_stats()
```

### 性能指标

性能监控记录：
- 查询耗时
- 成功/失败状态
- 时间戳
- 调用次数

---

## 🧪 性能测试

### 运行性能测试

```bash
# 运行所有性能测试
pytest -m performance

# 运行基准测试
pytest -m benchmark

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 性能测试类型

1. **查询优化测试** - 验证优化后的查询比原始查询更快
2. **缓存测试** - 验证缓存命中率
3. **性能监控测试** - 验证基准装饰器正确记录指标
4. **基准测试** - 测量API响应时间和数据库性能

### 性能目标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| API响应时间 | <100ms | 基准测试 |
| 数据库查询 | <50ms | 基准测试 |
| 缓存命中率 | >80% | 性能监控 |
| 并发处理 | 100+ | 并发测试 |

---

## 📈 性能最佳实践

### 1. 使用异步I/O

```python
# ✅ 异步查询
result = await db.execute(query)

# ❌ 同步查询（阻塞）
result = db.execute(query)
```

### 2. 批量操作

```python
# ✅ 批量插入
db.add_all([item1, item2, item3])
await db.commit()

# ❌ 逐个插入
for item in items:
    db.add(item)
    await db.commit()
```

### 3. 索引优化

```python
# 已添加的索引
__table_args__ = (
    Index('idx_stock_symbol_timestamp', 'symbol', 'timestamp'),
    Index('idx_indicator_symbol_type', 'symbol', 'indicator_type', 'timestamp'),
)
```

### 4. 分页查询

```python
# ✅ 使用分页
page = 1
size = 20
query.offset((page - 1) * size).limit(size)

# ❌ 一次获取所有数据
query.limit(10000)
```

### 5. 选择性查询

```python
# ✅ 只查询需要的字段
query = select(
    StockPrice.symbol,
    StockPrice.price
).where(...)

# ❌ 查询所有字段
query = select(StockPrice).where(...)
```

---

## 🔧 配置缓存

### 环境变量

```bash
# .env文件
REDIS_URL=redis://redis:6379/0
CACHE_TTL=300
```

### 禁用缓存（开发环境）

```python
# 在开发中可以临时禁用缓存
import os
if os.getenv("DISABLE_CACHE") == "true":
    # 绕过缓存装饰器
    pass
```

---

## 🚦 启动和关闭

### 初始化缓存

在 `main.py` 中已配置自动初始化：

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化缓存
    await init_db()
    await init_cache()

    yield

    # 关闭时清理缓存
    await close_cache()
    await close_db()
```

---

## 📊 监控仪表板

### 查看性能指标

```python
from app.core.performance import performance_monitor

@app.get("/performance-metrics")
async def get_performance_metrics():
    return performance_monitor.get_all_stats()
```

### 性能告警

在生产环境中设置告警：

```python
# 如果平均查询时间超过阈值
stats = performance_monitor.get_query_stats("critical_query")
if stats["avg"] > 0.5:  # 500ms
    # 发送告警
    send_alert("查询性能告警")
```

---

## 🛠️ 故障排除

### 缓存未命中

1. 检查Redis连接
2. 查看缓存键生成
3. 验证过期时间

### 查询慢

1. 检查数据库索引
2. 查看执行计划 (`EXPLAIN`)
3. 监控慢查询日志

### 连接池耗尽

1. 增加 `pool_size`
2. 检查连接泄漏
3. 优化长时间运行的查询

---

## 📚 参考资料

- [SQLAlchemy Async Performance](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [FastAPI Performance](https://fastapi.tiangolo.com/advanced/)
- [AsyncIO Best Practices](https://docs.python.org/3/library/asyncio-dev.html)

---

**记住**: 性能优化是一个持续的过程，定期监控和调整是关键！

