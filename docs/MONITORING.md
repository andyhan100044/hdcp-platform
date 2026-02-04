# 📊 HDCP 监控和可观测性指南

本文档说明HDCP模板中实施的监控和可观测性功能。

---

## 📋 监控概览

HDCP模板实施了全面的监控和可观测性系统：

- ✅ Prometheus指标
- ✅ 结构化日志
- ✅ 健康检查
- ✅ 告警管理
- ✅ 性能监控

---

## 🏥 健康检查

### 健康检查端点

| 端点 | 描述 |
|------|------|
| `/monitoring/health` | 全面健康检查 |
| `/monitoring/health/{component}` | 指定组件健康检查 |
| `/monitoring/ready` | Kubernetes就绪探针 |
| `/monitoring/live` | Kubernetes存活探针 |

### 内置健康检查

```python
from app.core.monitoring import health_checker

# 注册自定义健康检查
async def custom_check():
    return {
        "status": "healthy",
        "message": "Custom service is OK"
    }

health_checker.register_check("custom_service", custom_check)
```

### 健康检查状态

- **healthy** - 组件正常运行
- **degraded** - 组件部分功能受影响
- **unhealthy** - 组件无法正常工作

### 运行健康检查

```bash
# 获取完整健康报告
curl http://localhost:8000/monitoring/health

# 获取特定组件健康状态
curl http://localhost:8000/monitoring/health/memory

# Kubernetes探针
curl http://localhost:8000/monitoring/ready
curl http://localhost:8000/monitoring/live
```

### 健康检查响应示例

```json
{
  "status": "healthy",
  "timestamp": "2024-02-04T12:00:00",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful"
    },
    "memory": {
      "status": "healthy",
      "message": "Memory usage: 45%",
      "details": {
        "total": 16777216000,
        "used": 7549747200,
        "free": 9227468800,
        "percent": 45.0
      }
    }
  }
}
```

---

## 📊 Prometheus指标

### 指标端点

```
GET /monitoring/metrics
```

### 可用指标

#### HTTP指标

| 指标名称 | 类型 | 描述 |
|----------|------|------|
| `http_requests_total` | Counter | HTTP请求总数 |
| `http_request_duration_seconds` | Histogram | HTTP请求延迟 |
| `http_requests_active` | Gauge | 活跃HTTP请求数 |

#### 系统指标

| 指标名称 | 类型 | 描述 |
|----------|------|------|
| `memory_usage_bytes` | Gauge | 内存使用量 |
| `cpu_usage_percent` | Gauge | CPU使用率 |
| `db_pool_connections` | Gauge | 数据库连接池连接数 |

### 查看指标

```bash
# 获取所有指标
curl http://localhost:8000/monitoring/metrics

# 使用Prometheus查询
curl 'http://localhost:8000/monitoring/metrics' | grep http_requests_total
```

### 指标示例

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health",status_code="200"} 123.0

# HELP http_request_duration_seconds HTTP request latency in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="0.005"} 45.0
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="0.01"} 78.0
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="0.025"} 112.0
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="0.05"} 123.0
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="0.1"} 123.0
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="0.25"} 123.0
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="0.5"} 123.0
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="1.0"} 123.0
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="2.5"} 123.0
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="5.0"} 123.0
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="10.0"} 123.0
http_request_duration_seconds_bucket{method="GET",endpoint="/health",le="+Inf"} 123.0
http_request_duration_seconds_sum{method="GET",endpoint="/health"} 2.456
http_request_duration_seconds_count{method="GET",endpoint="/health"} 123.0

# HELP memory_usage_bytes Memory usage in bytes
# TYPE memory_usage_bytes gauge
memory_usage_bytes 7.5497472e+09
```

---

## 📝 结构化日志

### 日志中间件

```python
from app.core.monitoring import StructuredLoggingMiddleware

# 在main.py中已自动集成
app.add_middleware(StructuredLoggingMiddleware)
```

### 日志格式

结构化日志使用JSON格式：

```json
{
  "timestamp": "2024-02-04T12:00:00.123456",
  "name": "http_requests",
  "level": "INFO",
  "message": "Request completed",
  "event_type": "request_end",
  "method": "GET",
  "url": "http://localhost:8000/health",
  "status_code": 200,
  "duration": 0.045
}
```

### 使用日志记录器

```python
from app.core.monitoring import get_logger

logger = get_logger("my_service")

# 记录信息
logger.info("Service started", extra={"port": 8000})

# 记录警告
logger.warning("High memory usage", extra={"percent": 85})

# 记录错误
logger.error("Database connection failed", extra={
    "error": "connection refused",
    "host": "localhost"
}, exc_info=True)
```

### 日志级别

- **DEBUG** - 调试信息
- **INFO** - 一般信息
- **WARNING** - 警告
- **ERROR** - 错误

---

## 🚨 告警管理

### 告警规则

预定义告警规则：

```python
# 内存使用 > 85%
async def high_memory_alert():
    memory = psutil.virtual_memory()
    return memory.percent > 85

# CPU使用 > 80%
async def high_cpu_alert():
    return psutil.cpu_percent(interval=1) > 80

# 磁盘使用 > 90%
async def low_disk_alert():
    disk = psutil.disk_usage('/')
    return disk.percent > 90
```

### 告警端点

```bash
# 获取活跃告警
curl http://localhost:8000/monitoring/alerts

# 手动触发告警检查
curl -X POST http://localhost:8000/monitoring/alerts/check
```

### 添加自定义告警

```python
from app.core.monitoring import alert_manager

async def custom_alert():
    # 自定义告警条件
    return some_condition_is_true()

alert_manager.add_rule("custom_alert", custom_alert, "warning")
```

### 告警响应示例

```json
{
  "alerts": [
    {
      "name": "high_memory",
      "severity": "critical",
      "timestamp": "2024-02-04T12:00:00",
      "status": "firing"
    }
  ],
  "count": 1
}
```

---

## 🔍 监控集成

### Prometheus + Grafana

#### prometheus.yml

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'hdcp-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /monitoring/metrics
    scrape_interval: 5s
```

#### Grafana仪表板

导入预定义的Grafana仪表板：
- HTTP请求率
- 请求延迟
- 错误率
- 内存和CPU使用

### Jaeger (分布式追踪)

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 配置Jaeger
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 使用追踪
with tracer.start_as_current_span("db_query") as span:
    # 执行数据库查询
    result = await db.execute(query)
    span.set_attribute("db.statement", str(query))
```

---

## 🔧 配置

### 环境变量

```bash
# .env文件
LOG_LEVEL=INFO
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30
ALERT_CHECK_INTERVAL=60
```

### 在代码中配置

```python
from app.core.monitoring import get_logger, health_checker

# 设置日志级别
logger = get_logger("app", level="DEBUG")

# 注册健康检查
health_checker.register_check("custom", custom_check_function)
```

---

## 🧪 测试监控

### 运行监控测试

```bash
# 运行所有监控测试
pytest -m monitoring -v

# 运行特定测试
pytest tests/test_monitoring.py::TestHealthChecks::test_database_health_check -v
```

### 测试类型

1. **健康检查测试** - 验证所有健康检查正常工作
2. **日志测试** - 验证结构化日志输出
3. **告警测试** - 验证告警规则和触发
4. **指标测试** - 验证Prometheus指标收集
5. **集成测试** - 验证端到端监控流程

---

## 📈 最佳实践

### 1. 合理的告警阈值

```python
# ✅ 合理的阈值
MEMORY_WARNING = 80  # 80%
MEMORY_CRITICAL = 90  # 90%

# ❌ 过于严格
MEMORY_WARNING = 50  # 50%
```

### 2. 告警疲劳避免

- 设置有意义的告警
- 避免告警风暴
- 提供清晰的告警消息
- 包含解决步骤

### 3. 日志记录

```python
# ✅ 结构化日志
logger.info("User login", extra={
    "user_id": user.id,
    "ip": request.client.host
})

# ❌ 非结构化日志
logger.info(f"User {user.id} logged in from {request.client.host}")
```

### 4. 监控覆盖

- 所有关键路径
- 所有外部依赖
- 性能指标
- 业务指标

---

## 🚦 操作指南

### 检查系统状态

```bash
# 1. 检查健康状态
curl http://localhost:8000/monitoring/health

# 2. 查看指标
curl http://localhost:8000/monitoring/metrics

# 3. 检查告警
curl http://localhost:8000/monitoring/alerts

# 4. 查看详细状态
curl http://localhost:8000/monitoring/status
```

### 排查问题

#### 1. 高内存使用

```bash
# 检查内存健康检查
curl http://localhost:8000/monitoring/health/memory

# 查看内存指标
curl http://localhost:8000/monitoring/metrics | grep memory_usage_bytes
```

#### 2. 响应慢

```bash
# 查看请求延迟指标
curl http://localhost:8000/monitoring/metrics | grep http_request_duration_seconds

# 查看日志
tail -f logs/app.log | grep "duration"
```

#### 3. 数据库连接问题

```bash
# 检查数据库健康检查
curl http://localhost:8000/monitoring/health/database
```

---

## 📚 参考资料

- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Structured Logging](https://docs.python.org/3/library/logging.html)
- [Kubernetes Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

---

**记住**: 有效的监控是确保系统稳定运行的关键！

