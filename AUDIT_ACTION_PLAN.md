# 📋 HDCP 模板审计修复行动计划

基于 `CODE_AUDIT_REPORT.md` 的审计结果，本文档提供了具体的修复步骤和优先级。

---

## 🎯 快速概览

| 优先级 | 问题数量 | 预计工作量 | 影响 |
|--------|----------|------------|------|
| 🔴 紧急 | 3项 | 2-3周 | 高 |
| 🟡 高 | 5项 | 4-6周 | 中 |
| 🟢 中 | 4项 | 2-3月 | 低 |
| **总计** | **12项** | **3-4月** | - |

---

## 🔴 紧急修复项 (1-2周)

### 1. 添加数据库迁移机制

**问题**: 缺少Alembic迁移，版本控制困难

**修复步骤**:
```bash
# 步骤1: 安装Alembic
cd apps/api
pip install alembic

# 步骤2: 初始化
alembic init migrations

# 步骤3: 配置alembic.ini
cat > alembic.ini <<EOF
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql+asyncpg://hdcp_user:hdcp_password@postgres:5432/hdcp_db
EOF

# 步骤4: 创建初始迁移
alembic revision --autogenerate -m "Initial migration"

# 步骤5: 添加迁移服务到docker-compose.yml
```

**验证**:
```bash
docker-compose up -d
docker-compose exec api alembic upgrade head
```

---

### 2. 完善测试覆盖 (目标: >80%)

**问题**: 测试覆盖率 <2%

**修复步骤**:
```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 创建测试配置
cat > pytest.ini <<EOF
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = --cov=app --cov-report=html --cov-report=term
EOF

# 创建模型测试
cat > tests/test_models.py <<EOF
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.stock import StockPrice

@pytest.mark.asyncio
async def test_create_stock_price(db: AsyncSession):
    stock = StockPrice(
        symbol="AAPL",
        price=150.25,
        volume=1000000
    )
    db.add(stock)
    await db.commit()
    assert stock.id is not None
EOF

# 创建API测试
cat > tests/test_api.py <<EOF
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_stock():
    response = client.get("/api/stocks/AAPL")
    assert response.status_code in [200, 404]
EOF

# 运行测试
pytest
```

**验收标准**:
```bash
pytest --cov=app --cov-report=html
# 覆盖率 > 80%
```

---

### 3. 安全加固

#### 3.1 API密钥验证

**修复**:
```python
# apps/api/app/core/auth.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    api_key = credentials.credentials

    # 验证API密钥
    valid_key = os.getenv("VALID_API_KEYS", "").split(",")
    if api_key not in valid_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key
```

#### 3.2 凭证外部化

**修复**:
```bash
# 使用Docker Secrets
cat > .env.production <<EOF
POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password
JWT_SECRET_FILE=/run/secrets/jwt_secret
EOF

# docker-compose.prod.yml
secrets:
  postgres_password:
    file: ./secrets/postgres_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt

services:
  postgres:
    secrets:
      - postgres_password
```

#### 3.3 添加安全扫描

**修复**:
```bash
# 添加safety检查
pip install safety
echo "safety check" >> Makefile

# 添加trivy扫描
cat > Dockerfile.safety <<EOF
FROM python:3.11-slim
RUN pip install safety
COPY requirements.txt .
RUN safety check -r requirements.txt
EOF
```

---

## 🟡 高优先级修复项 (1个月)

### 4. 性能优化

#### 4.1 修复N+1查询

**问题**:
```python
# 当前: N+1查询
for stock in stocks:
    stock.indicators = await get_indicators(stock.id)
```

**修复**:
```python
# 使用JOIN或selectinload
from sqlalchemy.orm import selectinload

query = (
    select(StockPrice)
    .options(selectinload(StockPrice.indicators))
    .where(StockPrice.symbol == symbol)
)
stocks = await db.execute(query)
stocks = stocks.scalars().all()
```

#### 4.2 配置连接池

**修复**:
```python
# apps/api/app/database.py
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=20,          # 连接池大小
    max_overflow=30,       # 最大溢出
    pool_pre_ping=True,    # 预ping
    pool_recycle=3600,     # 连接回收时间
    pool_timeout=30        # 获取连接超时
)
```

#### 4.3 GraphQL DataLoader

**修复**:
```python
# apps/api/app/graphql/dataloaders.py
from dataloader import DataLoader

class StockLoader(DataLoader):
    async def batch_load_fn(self, symbols):
        stocks = await self.db.execute(
            select(StockPrice).where(StockPrice.symbol.in_(symbols))
        )
        return [stocks.scalars().all()]

# apps/api/app/graphql/schema.py
from .dataloaders import StockLoader

class StockType(SQLAlchemyObjectType):
    class Meta:
        model = StockPrice
        interfaces = (graphene.relay.Node,)

    indicators = graphene.List(IndicatorType)

    def resolve_indicators(self, info):
        return info.context["loaders"]["stock_loader"].load(self.id)
```

---

### 5. 监控完善

#### 5.1 集成APM (Jaeger)

**修复**:
```python
# apps/api/app/monitoring.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# 配置Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

# 初始化追踪
def setup_tracing(app):
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor.instrument()
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )

# 在main.py中使用
setup_tracing(app)
```

#### 5.2 结构化日志

**修复**:
```python
# apps/api/app/logging.py
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# 使用
logger = structlog.get_logger()
logger.info("cache_read_failed", error=str(e), endpoint="/api/stocks")
```

#### 5.3 告警配置

**修复**:
```yaml
# monitoring/alerts.yml
groups:
  - name: hdcp_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_activity_count > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: High database connections
```

---

### 6. CI/CD流水线

**修复**:
```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

      - name: Security scan
        run: |
          pip install safety
          safety check

      - name: Build Docker images
        run: |
          docker-compose build

      - name: Deploy to staging
        if: github.ref == 'refs/heads/develop'
        run: |
          # 部署到staging环境
          kubectl apply -f k8s/staging/

      - name: Deploy to production
        if: github.ref == 'refs/heads/main'
        run: |
          # 部署到生产环境
          kubectl apply -f k8s/production/
```

---

### 7. CORS安全配置

**修复**:
```python
# apps/api/app/config/settings.py
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    # ...

    # 改为具体域名
    cors_origins: List[AnyHttpUrl] = [
        "https://yourdomain.com",
        "https://admin.yourdomain.com",
        "https://api.yourdomain.com",
    ]

    @validator('cors_origins', pre=True)
    def assemble_cors_origins(cls, v):
        # 解析环境变量
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
```

---

## 🟢 中等优先级修复项 (2-3个月)

### 8. 添加消息队列 (Celery)

**修复**:
```python
# apps/api/app/tasks.py
from celery import Celery

celery_app = Celery('hdcp', broker='redis://redis:6379/0')

@celery_app.task
def update_stock_prices(symbols: List[str]):
    """异步更新股价"""
    for symbol in symbols:
        # 获取股价
        price = fetch_stock_price(symbol)
        # 保存到数据库
        save_stock_price(symbol, price)

# 在路由中使用
@router.post("/update")
async def trigger_price_update(symbols: List[str]):
    update_stock_prices.delay(symbols)
    return {"status": "queued"}
```

---

### 9. 性能测试

**修复**:
```python
# tests/performance/test_load.py
from locust import HttpUser, task, between

class StockApiUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_stock(self):
        self.client.get("/api/stocks/AAPL")

    @task
    def get_history(self):
        self.client.get("/api/stocks/AAPL/history?limit=100")

# 运行
# locust -f tests/performance/test_load.py
```

---

### 10. Kubernetes支持

**修复**:
```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hdcp-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hdcp-api
  template:
    metadata:
      labels:
        app: hdcp-api
    spec:
      containers:
      - name: api
        image: hdcp-api:latest
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: hdcp-secrets
              key: database-url
```

---

## 📅 实施时间表

### 周 1-2: 紧急修复
- [ ] 数据库迁移机制
- [ ] 测试覆盖 (>80%)
- [ ] 安全加固

### 周 3-4: 高优先级
- [ ] 性能优化 (N+1, 连接池)
- [ ] 监控 (APM, 日志)
- [ ] CI/CD流水线

### 月 2-3: 中优先级
- [ ] 消息队列
- [ ] 性能测试
- [ ] Kubernetes支持

---

## ✅ 验收标准

### 每个修复项的验收标准:

1. **数据库迁移**
   - [ ] Alembic集成完成
   - [ ] 迁移脚本可运行
   - [ ] 版本历史正确

2. **测试覆盖**
   - [ ] 覆盖率 > 80%
   - [ ] 所有API端点有测试
   - [ ] 所有模型有测试

3. **安全加固**
   - [ ] API密钥验证
   - [ ] Secrets外部化
   - [ ] 安全扫描通过

4. **性能优化**
   - [ ] 无N+1查询
   - [ ] 连接池配置
   - [ ] 性能测试通过

5. **监控完善**
   - [ ] APM集成
   - [ ] 结构化日志
   - [ ] 告警配置

6. **CI/CD**
   - [ ] GitHub Actions配置
   - [ ] 自动测试
   - [ ] 自动部署

---

## 📊 资源需求

### 人力投入
- **1名后端工程师**: 2周
- **1名前端工程师**: 1周
- **1名DevOps工程师**: 1周
- **1名QA工程师**: 1周

### 外部工具
- **Jaeger APM**: 免费
- **Codecov**: 免费 (开源项目)
- **GitHub Actions**: 2000分钟/月 (免费额度)

---

## 🎯 成功指标

| 指标 | 当前 | 目标 | 测量方式 |
|------|------|------|----------|
| 测试覆盖率 | <2% | >80% | pytest --cov |
| 安全漏洞 | - | 0个高危 | safety audit |
| 响应时间 | - | <200ms | Locust测试 |
| 错误率 | - | <0.1% | Prometheus |
| 可用性 | - | 99.9% | Uptime监控 |

---

## 📞 支持与帮助

### 实施过程中遇到问题?

**Slack频道**: #hdcp-improvements
**文档**: `/docs/improvements`
**代码审查**: 所有PR需2人审查

### 定期回顾

- **每周回顾**: 进度检查
- **每两周回顾**: 验收标准评估
- **每月回顾**: 整体进度评估

---

**记住**: 逐步实施，优先处理高风险项，确保每个修复都经过充分测试！
