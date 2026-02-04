# 🔒 HDCP 安全指南

本指南说明如何在HDCP模板中实现和维护安全。

---

## 📋 安全概览

HDCP模板实施了多层安全机制：

- ✅ API密钥认证
- ✅ JWT令牌认证
- ✅ 安全头
- ✅ CSRF保护
- ✅ SQL注入防护
- ✅ 限流
- ✅ 输入验证
- ✅ 安全扫描

---

## 🔐 认证与授权

### API密钥认证

#### 创建API密钥

```python
from app.core.security import SecurityManager

# 创建API密钥
api_key = SecurityManager.create_api_key(
    name="My Application",
    user_id="user123",
    scopes=["read", "write"],  # 可选作用域
    expires_in_days=30  # 可选过期天数
)

print(f"Your API Key: {api_key}")
```

#### 使用API密钥

```bash
# 在请求头中使用
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.example.com/data
```

#### 验证API密钥

```python
from app.core.security import get_current_api_key_user

async def get_data(user_data = Depends(get_current_api_key_user)):
    # user_data 包含用户信息
    return {"user_id": user_data["user_id"]}
```

#### 撤销API密钥

```python
# 撤销API密钥
SecurityManager.revoke_api_key(api_key)
```

### JWT令牌认证

#### 创建令牌

```python
from app.core.security import SecurityManager

data = {"user_id": "123", "scopes": ["read", "write"]}
token = SecurityManager.create_access_token(
    data,
    expires_delta=timedelta(minutes=30)  # 可选过期时间
)
```

#### 验证令牌

```python
from app.core.security import get_current_user

async def protected_endpoint(user = Depends(get_current_user)):
    # user 包含令牌数据
    return {"user_id": user["user_id"]}
```

#### 作用域检查

```python
from app.core.security import check_scope

async def admin_endpoint(
    user = Depends(check_scope("admin"))
):
    # 只有具有admin作用域的用户可以访问
    return {"message": "Admin only"}
```

---

## 🛡️ 中间件安全

### 中间件集成

安全中间件已集成到主应用程序中 (`apps/api/app/main.py`)：

```python
from app.middleware.security import (
    SecurityHeadersMiddleware,
    CSRFProtectionMiddleware,
    SQLInjectionProtectionMiddleware,
    RateLimitByUserMiddleware,
    InputValidationMiddleware,
)

# 添加安全中间件
if security_config.settings.SECURITY_HEADERS_ENABLED:
    app.add_middleware(SecurityHeadersMiddleware)

if security_config.settings.CSRF_PROTECTION_ENABLED:
    app.add_middleware(CSRFProtectionMiddleware)

app.add_middleware(SQLInjectionProtectionMiddleware)
app.add_middleware(InputValidationMiddleware)
app.add_middleware(
    RateLimitByUserMiddleware,
    requests_per_minute=security_config.settings.RATE_LIMIT_PER_MINUTE
)
```

### 安全头中间件

自动添加的安全头：
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

生产环境额外添加：
- `Strict-Transport-Security`
- `Content-Security-Policy`

### CSRF保护

自动检查POST、PUT、DELETE、PATCH请求的CSRF令牌。

跳过检查的路径：
- `/api/webhooks`
- `/api/auth/login`
- `/api/auth/register`

#### 使用CSRF令牌

```html
<!-- 在HTML表单中 -->
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <input type="text" name="username">
    <input type="password" name="password">
</form>
```

### SQL注入防护

自动检测和阻止：
- UNION SELECT
- DROP TABLE
- DELETE FROM
- INSERT INTO
- UPDATE SET
- ALTER TABLE
- CREATE TABLE
- EXEC
- EXECUTE
- 1=1等布尔注入

### 限流

默认配置：
- 每分钟100请求（基于用户ID或IP地址）
- 自动清理过期记录
- 响应头包含限流信息：
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`

### 输入验证

自动检测和阻止：
- XSS攻击（`<script>`, `javascript:`, `onload=`, etc.）
- 路径遍历攻击（`../`, `..\\`, `%2e%2e%2f`, etc.）
- 恶意输入模式

---

## 🔒 配置安全

### 环境变量

```bash
# .env文件
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_KEY_EXPIRE_DAYS=30
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
ENVIRONMENT=production
```

### 安全配置类

```python
from app.config.security import SecurityConfig, SecuritySettings

settings = SecuritySettings()
config = SecurityConfig(settings)

# 检查是否为生产环境
if config.is_production():
    print("Running in production mode")

# 获取CORS设置
cors_settings = config.get_cors_settings()

# 验证密码强度
is_valid, errors = config.validate_password_strength(password)
```

---

## 🔍 安全扫描

### 运行安全扫描

```bash
# 使用脚本
bash scripts/security-scan.sh

# 或手动运行
cd apps/api

# 1. 依赖安全扫描
pip install safety
safety check

# 2. 代码安全扫描
pip install bandit
bandit -r app/

# 3. 高级安全扫描
pip install semgrep
semgrep --config=auto app/
```

### 扫描工具

| 工具 | 用途 | 命令 |
|------|------|------|
| **Safety** | 依赖漏洞扫描 | `safety check` |
| **Bandit** | Python安全lint | `bandit -r app/` |
| **Semgrep** | 静态分析 | `semgrep --config=auto app/` |

---

## 📝 编写安全测试

### 测试API密钥

```python
from app.core.security import SecurityManager

def test_api_key_creation():
    """测试API密钥创建"""
    api_key = SecurityManager.create_api_key(
        name="Test",
        user_id="123"
    )

    assert api_key is not None
    assert len(api_key) > 0

def test_api_key_verification():
    """测试API密钥验证"""
    api_key = SecurityManager.create_api_key(
        name="Test",
        user_id="123"
    )

    user_data = SecurityManager.verify_api_key(api_key)
    assert user_data is not None
    assert user_data["user_id"] == "123"

def test_api_key_revocation():
    """测试API密钥撤销"""
    api_key = SecurityManager.create_api_key(
        name="Test",
        user_id="123"
    )

    # 撤销密钥
    SecurityManager.revoke_api_key(api_key)

    # 验证密钥已失效
    assert SecurityManager.verify_api_key(api_key) is None
```

### 测试JWT令牌

```python
from app.core.security import SecurityManager

def test_jwt_creation():
    """测试JWT令牌创建"""
    data = {"user_id": "123"}
    token = SecurityManager.create_access_token(data)

    assert token is not None

def test_jwt_verification():
    """测试JWT令牌验证"""
    data = {"user_id": "123"}
    token = SecurityManager.create_access_token(data)

    payload = SecurityManager.verify_access_token(token)
    assert payload is not None
    assert payload["user_id"] == "123"

def test_jwt_expiration():
    """测试JWT令牌过期"""
    from datetime import datetime, timedelta

    # 创建过期令牌
    expire = datetime.utcnow() - timedelta(minutes=1)
    to_encode = {"user_id": "123", "exp": expire}

    from jose import jwt
    expired_token = jwt.encode(
        to_encode,
        "secret",
        algorithm="HS256"
    )

    payload = SecurityManager.verify_access_token(expired_token)
    assert payload is None
```

---

## ⚠️ 安全最佳实践

### 1. 密码安全

```python
from app.core.security import SecurityManager, is_strong_password

# 检查密码强度
is_valid, errors = is_strong_password(password)
if not is_valid:
    for error in errors:
        print(f"Password error: {error}")

# 哈希密码
hashed_password = SecurityManager.get_password_hash(password)

# 验证密码
is_valid = SecurityManager.verify_password(password, hashed_password)
```

### 2. 敏感数据处理

```python
from app.core.security import hash_sensitive_data, verify_sensitive_data

# 哈希敏感数据
data = "sensitive_info"
hashed, salt = hash_sensitive_data(data)

# 验证敏感数据
is_valid = verify_sensitive_data(data, hashed, salt)
assert is_valid is True
```

### 3. 令牌管理

```python
from app.core.security import SecurityManager

# 创建令牌
token = SecurityManager.create_access_token({"user_id": "123"})

# 撤销令牌
SecurityManager.revoke_token(token)

# 检查令牌是否已撤销
is_revoked = SecurityManager.is_token_revoked(token)
assert is_revoked is True
```

### 4. API密钥管理

```python
from app.core.security import SecurityManager

# 创建API密钥
api_key = SecurityManager.create_api_key(
    name="My App",
    user_id="123",
    scopes=["read", "write"]
)

# 验证API密钥
user_data = SecurityManager.verify_api_key(api_key)
if user_data:
    print(f"User: {user_data['user_id']}")
    print(f"Scopes: {user_data['scopes']}")

# 撤销API密钥
SecurityManager.revoke_api_key(api_key)
```

---

## 🚨 常见安全威胁

### 1. SQL注入

**问题**: 恶意用户通过输入破坏SQL查询

**解决方案**:
- 使用ORM (SQLAlchemy)
- 参数化查询
- 输入验证
- SQL注入防护中间件

```python
# ❌ 不安全的代码
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ 安全的代码
query = "SELECT * FROM users WHERE id = :id"
result = await db.execute(query, {"id": user_id})
```

### 2. XSS攻击

**问题**: 恶意脚本注入到网页

**解决方案**:
- 输入验证
- 输出编码
- CSP头
- XSS防护中间件

```python
from markupsafe import Markup, escape

# 转义用户输入
user_input = "<script>alert('XSS')</script>"
safe_input = escape(user_input)
```

### 3. CSRF攻击

**问题**: 恶意网站利用用户身份发起请求

**解决方案**:
- CSRF令牌
- SameSite Cookie
- CSRF防护中间件

```python
# 生成CSRF令牌
from app.middleware.security import CSRFProtectionMiddleware
csrf_token = CSRFProtectionMiddleware.generate_csrf_token(session_id)

# 验证CSRF令牌
if request.headers.get("X-CSRF-Token") != csrf_token:
    raise HTTPException(status_code=403, detail="Invalid CSRF token")
```

### 4. 会话劫持

**问题**: 攻击者窃取用户会话令牌

**解决方案**:
- HTTPS传输
- 安全Cookie设置
- 令牌过期
- 令牌撤销

```python
# 设置安全Cookie
response.set_cookie(
    key="session_id",
    value=session_id,
    secure=True,  # 仅HTTPS
    httponly=True,  # 防止JS访问
    samesite="strict"  # 防止CSRF
)
```

---

## 📚 参考资料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI安全指南](https://fastapi.tiangolo.com/tutorial/security/)
- [Python安全手册](https://python-security.readthedocs.io/)

---

## 💬 支持

如遇到安全问题：

1. 查看日志: `tail -f logs/security.log`
2. 运行扫描: `bash scripts/security-scan.sh`
3. 查看文档: [安全指南](SECURITY.md)
4. 创建Issue: 在项目中提交安全问题

---

**记住**: 安全是一个持续的过程，请定期更新依赖、扫描代码和更新安全配置！
