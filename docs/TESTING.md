# 🧪 HDCP 测试指南

本指南说明如何在HDCP模板中编写和运行测试。

---

## 📋 测试概览

HDCP模板使用**pytest**作为测试框架，具有以下特性：

- ✅ 单元测试 (模型测试)
- ✅ 集成测试 (API测试)
- ✅ 异步测试支持
- ✅ 代码覆盖率报告
- ✅ 测试标记 (markers)
- ✅ 并行测试

---

## 🏃‍♂️ 快速开始

### 运行所有测试

```bash
# 使用脚本运行
bash scripts/run-tests.sh

# 或手动运行
cd apps/api
pytest tests/ -v --cov=app --cov-report=html
```

### 运行特定类型测试

```bash
# 单元测试
make test-unit
# 或
pytest tests/test_models.py -v

# 集成测试
make test-integration
# 或
pytest tests/test_api.py -v -m integration

# API测试
make test-api
# 或
pytest tests/test_api.py -v -m api
```

### 生成覆盖率报告

```bash
# HTML报告
make coverage-report
# 或
pytest tests/ --cov=app --cov-report=html

# 查看报告
open apps/api/htmlcov/index.html
```

---

## 📁 测试结构

```
apps/api/tests/
├── conftest.py              # pytest配置和fixtures
├── test_models.py           # 模型测试
├── test_api.py              # API测试
└── test_performance.py      # 性能测试 (可选)
```

---

## 🧩 Fixtures

### 数据库Fixture

```python
# conftest.py
@pytest.fixture
async def db_session(test_db):
    """创建测试数据库会话"""
    # 使用步骤:
    # 1. 测试开始时创建会话
    # 2. 测试结束时清理
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    # 清理
    await session.close()
    await transaction.rollback()
    await connection.close()
```

### HTTP客户端Fixture

```python
# conftest.py
@pytest.fixture
async def client(db_session):
    """创建测试客户端"""
    # 重写依赖
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
```

### 示例数据Fixture

```python
# conftest.py
@pytest.fixture
def sample_stock_data():
    """示例股票数据"""
    return {
        "symbol": "AAPL",
        "price": 150.25,
        "volume": 1000000,
        "price_change": 2.50,
        "price_change_percent": 1.67,
        "source": "TEST"
    }
```

---

## ✅ 模型测试

### 测试示例

```python
from app.models.stock import StockPrice
from datetime import datetime

class TestStockPriceModel:
    """测试股票价格模型"""

    @pytest.mark.unit
    def test_stock_price_creation(self, db_session):
        """测试创建股票价格"""
        stock = StockPrice(
            symbol="AAPL",
            price=150.25,
            volume=1000000,
            timestamp=datetime.utcnow()
        )
        db_session.add(stock)
        db_session.commit()

        assert stock.id is not None
        assert stock.symbol == "AAPL"
        assert stock.price == 150.25

    @pytest.mark.unit
    def test_stock_price_indexes(self, db_session):
        """测试股票价格索引"""
        from sqlalchemy import inspect

        stock = StockPrice(
            symbol="GOOGL",
            price=2500.00,
            volume=500000,
            timestamp=datetime.utcnow()
        )
        db_session.add(stock)
        db_session.commit()

        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('stock_prices')
        index_names = [idx['name'] for idx in indexes]

        assert 'idx_stock_symbol_timestamp' in index_names
```

---

## 🔌 API测试

### 测试示例

```python
from httpx import AsyncClient
from datetime import datetime

class TestStockAPI:
    """测试股票API端点"""

    @pytest.mark.api
    @pytest.mark.integration
    async def test_create_stock(self, client: AsyncClient):
        """测试创建股票"""
        stock_data = {
            "symbol": "AAPL",
            "price": 150.25,
            "volume": 1000000,
            "price_change": 2.50,
            "price_change_percent": 1.67,
            "source": "TEST",
            "timestamp": datetime.utcnow().isoformat()
        }

        response = await client.post("/api/stocks", json=stock_data)
        assert response.status_code == 200

        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["price"] == 150.25

    @pytest.mark.api
    @pytest.mark.integration
    async def test_get_stock(self, client: AsyncClient):
        """测试获取股票"""
        response = await client.get("/api/stocks/AAPL")
        assert response.status_code == 200

        data = response.json()
        assert data["symbol"] == "AAPL"
```

---

## 📊 测试标记

### 标记类型

```python
@pytest.mark.unit           # 单元测试
@pytest.mark.integration    # 集成测试
@pytest.mark.api            # API测试
@pytest.mark.database       # 数据库测试
@pytest.mark.slow          # 慢速测试
@pytest.mark.performance    # 性能测试
```

### 运行标记测试

```bash
# 运行单元测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"

# 运行集成和API测试
pytest -m "integration or api"
```

---

## 📝 编写测试指南

### 1. 命名约定

```python
# 类名: Test + 模型名 + 功能
class TestStockPriceModel:
    # 方法名: test_ + 功能 + 描述
    def test_stock_price_creation(self):
    def test_stock_price_indexes(self):
```

### 2. AAA模式

```python
def test_example(self, db_session):
    # Arrange - 准备
    data = {"symbol": "AAPL"}

    # Act - 执行
    response = await client.post("/api/stocks", json=data)

    # Assert - 断言
    assert response.status_code == 200
```

### 3. 断言最佳实践

```python
# ✅ 好的断言
assert response.status_code == 200
assert data["symbol"] == "AAPL"
assert stock.id is not None
assert len(stocks) > 0

# ❌ 避免的断言
assert True  # 无用的断言
assert response.json()  # 不检查内容
```

### 4. 测试隔离

```python
# ✅ 每个测试独立
def test_create_stock_1(self, db_session):
    stock = create_stock(db_session, symbol="AAPL")
    assert stock.symbol == "AAPL"

def test_create_stock_2(self, db_session):
    stock = create_stock(db_session, symbol="GOOGL")
    assert stock.symbol == "GOOGL"

# ❌ 测试依赖
def test_create_stock_1(self, db_session):
    stock = create_stock(db_session, symbol="AAPL")
    assert stock.symbol == "AAPL"

def test_update_stock(self, db_session):
    # 依赖前一个测试的数据 - 不好！
    update_stock(db_session, "AAPL", price=200)
```

---

## 🛠️ 配置

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=80
    -v
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    api: API tests
    database: Database tests
```

---

## 📈 覆盖率报告

### 生成报告

```bash
# 生成HTML报告
pytest tests/ --cov=app --cov-report=html

# 生成XML报告 (CI/CD)
pytest tests/ --cov=app --cov-report=xml

# 生成所有格式
pytest tests/ --cov=app \
    --cov-report=html \
    --cov-report=term \
    --cov-report=xml
```

### 查看报告

```bash
# HTML报告
open apps/api/htmlcov/index.html

# 命令行报告
pytest tests/ --cov=app --cov-report=term

# 覆盖率阈值
pytest tests/ --cov=app --cov-fail-under=80
```

---

## 🚀 性能测试

### 安装基准测试

```bash
pip install pytest-benchmark
```

### 性能测试示例

```python
class TestPerformance:
    """性能测试"""

    @pytest.mark.performance
    def test_create_stock_performance(self, db_session):
        """测试创建股票性能"""
        def create_stock():
            stock = StockPrice(
                symbol="PERF",
                price=100.00,
                volume=1000000,
                timestamp=datetime.utcnow()
            )
            db_session.add(stock)
            db_session.commit()

        # 运行100次创建操作
        result = pytest.benchmark(create_stock, rounds=100)
        assert result.stats['mean'] < 0.01  # 平均小于10ms
```

---

## 🔍 调试测试

### 使用pdb

```python
def test_with_debug(self, db_session):
    stock = StockPrice(
        symbol="DEBUG",
        price=100.00,
        volume=1000000,
        timestamp=datetime.utcnow()
    )
    db_session.add(stock)
    db_session.commit()

    # 调试断点
    import pdb; pdb.set_trace()  # 在此处暂停

    assert stock.symbol == "DEBUG"
```

### 使用--pdb

```bash
# 测试失败时进入调试器
pytest tests/test_models.py --pdb

# 第一个失败后停止
pytest tests/ --pdbcls=IPython.terminal.debugger:Pdb
```

---

## 🐛 常见问题

### 1. 异步测试问题

```python
# ❌ 错误的异步测试
@pytest.mark.asyncio
async def test_slow_operation():
    result = await slow_function()
    assert result is not None

# ✅ 正确的异步测试
@pytest.mark.asyncio
async def test_slow_operation():
    result = await slow_function()
    assert result is not None
```

### 2. 数据库会话问题

```python
# ❌ 没有清理数据库
def test_create_stock(self, db_session):
    stock = create_stock(db_session, symbol="AAPL")
    assert stock.id is not None
    # 没有清理，可能影响其他测试

# ✅ 正确使用fixture
def test_create_stock(self, db_session):
    stock = create_stock(db_session, symbol="AAPL")
    assert stock.id is not None
    # fixture会自动清理
```

### 3. 测试数据隔离

```python
# ❌ 共享测试数据
class TestStockAPI:
    @pytest.fixture
    def stock_data(self):
        return {"symbol": "AAPL", "price": 100}

    def test_create_stock_1(self, stock_data):
        # 可能影响其他测试

# ✅ 使用参数化
@pytest.mark.parametrize("symbol,price", [
    ("AAPL", 100),
    ("GOOGL", 200),
    ("MSFT", 300)
])
def test_create_stock(self, symbol, price):
    stock_data = {"symbol": symbol, "price": price}
    # 每个参数独立测试
```

---

## 📚 参考资料

- [pytest文档](https://docs.pytest.org/)
- [pytest-asyncio文档](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov文档](https://pytest-cov.readthedocs.io/)
- [FastAPI测试指南](https://fastapi.tiangolo.com/tutorial/testing/)

---

## 💬 支持

如果您遇到测试问题：

1. 检查日志: `pytest tests/ -v --tb=long`
2. 查看文档: [pytest文档](https://docs.pytest.org/)
3. 创建Issue: 在项目中提交问题

---

**记住**: 测试是代码质量的重要保障，请编写充分的测试！
