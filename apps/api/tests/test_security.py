"""
Security Tests
测试安全功能
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.core.security import SecurityManager
from app.config.security import SecuritySettings, SecurityConfig


class TestSecurityManager:
    """测试安全管理器"""

    def test_create_api_key(self):
        """测试创建API密钥"""
        api_key = SecurityManager.create_api_key(
            name="Test Key",
            user_id="user123",
            scopes=["read", "write"]
        )

        assert api_key is not None
        assert len(api_key) > 0

        # 验证密钥可以验证
        user_data = SecurityManager.verify_api_key(api_key)
        assert user_data is not None
        assert user_data["name"] == "Test Key"
        assert user_data["user_id"] == "user123"
        assert "read" in user_data["scopes"]
        assert "write" in user_data["scopes"]

    def test_verify_invalid_api_key(self):
        """测试验证无效API密钥"""
        invalid_key = "invalid_key_123"
        user_data = SecurityManager.verify_api_key(invalid_key)
        assert user_data is None

    def test_revoke_api_key(self):
        """测试撤销API密钥"""
        api_key = SecurityManager.create_api_key(
            name="Test Key",
            user_id="user123"
        )

        # 验证密钥
        assert SecurityManager.verify_api_key(api_key) is not None

        # 撤销密钥
        assert SecurityManager.revoke_api_key(api_key) is True

        # 验证密钥已失效
        assert SecurityManager.verify_api_key(api_key) is None

    def test_create_access_token(self):
        """测试创建访问令牌"""
        data = {"user_id": "123", "username": "testuser"}
        token = SecurityManager.create_access_token(data)

        assert token is not None
        assert len(token) > 0

        # 验证令牌
        payload = SecurityManager.verify_access_token(token)
        assert payload is not None
        assert payload["user_id"] == "123"
        assert payload["username"] == "testuser"

    def test_verify_invalid_token(self):
        """测试验证无效令牌"""
        invalid_token = "invalid_token_123"
        payload = SecurityManager.verify_access_token(invalid_token)
        assert payload is None

    def test_token_expiration(self):
        """测试令牌过期"""
        data = {"user_id": "123"}
        # 创建已过期的令牌
        expire = datetime.utcnow() - timedelta(minutes=1)
        to_encode = data.copy()
        to_encode.update({"exp": expire})

        from jose import jwt
        expired_token = jwt.encode(
            to_encode,
            "secret",
            algorithm="HS256"
        )

        payload = SecurityManager.verify_access_token(expired_token)
        assert payload is None

    def test_revoke_token(self):
        """测试撤销令牌"""
        data = {"user_id": "123"}
        token = SecurityManager.create_access_token(data)

        # 验证令牌有效
        assert SecurityManager.verify_access_token(token) is not None

        # 撤销令牌
        SecurityManager.revoke_token(token)

        # 验证令牌已撤销
        assert SecurityManager.is_token_revoked(token) is True
        assert SecurityManager.verify_access_token(token) is None

    def test_password_hash(self):
        """测试密码哈希"""
        password = "SecurePassword123!"
        hashed = SecurityManager.get_password_hash(password)

        assert hashed is not None
        assert hashed != password

        # 验证密码
        assert SecurityManager.verify_password(password, hashed) is True
        assert SecurityManager.verify_password("wrong_password", hashed) is False

    def test_generate_secure_token(self):
        """测试生成安全令牌"""
        token1 = SecurityManager.generate_secure_token()
        token2 = SecurityManager.generate_secure_token()

        assert token1 is not None
        assert token2 is not None
        assert token1 != token2
        assert len(token1) > 20

    def test_hash_sensitive_data(self):
        """测试哈希敏感数据"""
        data = "sensitive_info"
        hashed, salt = SecurityManager.hash_sensitive_data(data)

        assert hashed is not None
        assert salt is not None
        assert hashed != data

        # 验证数据
        assert SecurityManager.verify_sensitive_data(data, hashed, salt) is True
        assert SecurityManager.verify_sensitive_data("wrong_data", hashed, salt) is False

    def test_is_strong_password(self):
        """测试密码强度检查"""
        # 强密码
        strong_password = "StrongP@ssw0rd"
        is_valid, errors = SecurityManager.is_strong_password(strong_password)
        assert is_valid is True
        assert len(errors) == 0

        # 弱密码 - 太短
        weak_password = "123"
        is_valid, errors = SecurityManager.is_strong_password(weak_password)
        assert is_valid is False
        assert "at least 8 characters" in errors[0]

        # 弱密码 - 没有大写
        weak_password = "lowercase123!"
        is_valid, errors = SecurityManager.is_strong_password(weak_password)
        assert is_valid is False
        assert "uppercase" in errors[0]


class TestSecurityConfig:
    """测试安全配置"""

    def test_is_production(self, monkeypatch):
        """测试生产环境检查"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        config = SecurityConfig(SecuritySettings(SECRET_KEY="test"))

        assert config.is_production() is True

    def test_is_development(self, monkeypatch):
        """测试开发环境检查"""
        monkeypatch.setenv("ENVIRONMENT", "development")
        config = SecurityConfig(SecuritySettings(SECRET_KEY="test"))

        assert config.is_production() is False

    def test_get_allowed_origins(self, monkeypatch):
        """测试获取允许的源"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("CORS_ORIGINS", "https://example.com,https://api.example.com")

        config = SecurityConfig(SecuritySettings(SECRET_KEY="test"))

        origins = config.get_allowed_origins()
        assert "https://example.com" in origins
        assert "https://api.example.com" in origins

    def test_get_cors_settings(self):
        """测试获取CORS设置"""
        config = SecurityConfig(SecuritySettings(
            SECRET_KEY="test",
            CORS_ORIGINS=["http://localhost:3000"],
            CORS_CREDENTIALS=True
        ))

        cors_settings = config.get_cors_settings()
        assert cors_settings["allow_origins"] == ["http://localhost:3000"]
        assert cors_settings["allow_credentials"] is True

    def test_get_security_headers(self, monkeypatch):
        """测试获取安全头"""
        monkeypatch.setenv("ENVIRONMENT", "development")
        config = SecurityConfig(SecuritySettings(SECRET_KEY="test"))

        headers = config.get_security_headers()
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers

    def test_validate_password_strength(self):
        """测试密码强度验证"""
        config = SecurityConfig(SecuritySettings(
            SECRET_KEY="test",
            PASSWORD_MIN_LENGTH=8,
            PASSWORD_REQUIRE_UPPERCASE=True,
            PASSWORD_REQUIRE_LOWERCASE=True,
            PASSWORD_REQUIRE_DIGITS=True,
            PASSWORD_REQUIRE_SPECIAL=True
        ))

        # 强密码
        is_valid, errors = config.validate_password_strength("StrongP@ssw0rd")
        assert is_valid is True
        assert len(errors) == 0

        # 弱密码
        is_valid, errors = config.validate_password_strength("weak")
        assert is_valid is False
        assert len(errors) > 0

    def test_get_session_settings(self, monkeypatch):
        """测试获取会话设置"""
        monkeypatch.setenv("ENVIRONMENT", "production")
        config = SecurityConfig(SecuritySettings(
            SECRET_KEY="test",
            SESSION_COOKIE_SECURE=True
        ))

        session_settings = config.get_session_settings()
        assert session_settings["timeout_minutes"] == 60
        assert session_settings["cookie_secure"] is True
        assert session_settings["cookie_httponly"] is True


class TestSecurityIntegration:
    """集成安全测试"""

    @pytest.mark.security
    def test_api_key_authentication_flow(self):
        """测试API密钥认证流程"""
        # 创建API密钥
        api_key = SecurityManager.create_api_key(
            name="Test Key",
            user_id="user123",
            scopes=["read"]
        )

        # 验证API密钥
        user_data = SecurityManager.verify_api_key(api_key)
        assert user_data is not None
        assert user_data["user_id"] == "user123"

        # 撤销API密钥
        SecurityManager.revoke_api_key(api_key)

        # 验证API密钥已失效
        user_data = SecurityManager.verify_api_key(api_key)
        assert user_data is None

    @pytest.mark.security
    def test_jwt_token_flow(self):
        """测试JWT令牌流程"""
        # 创建令牌
        data = {"user_id": "123", "scopes": ["read", "write"]}
        token = SecurityManager.create_access_token(data)

        # 验证令牌
        payload = SecurityManager.verify_access_token(token)
        assert payload is not None
        assert payload["user_id"] == "123"
        assert "read" in payload["scopes"]
        assert "write" in payload["scopes"]

        # 撤销令牌
        SecurityManager.revoke_token(token)

        # 验证令牌已撤销
        assert SecurityManager.is_token_revoked(token) is True


class TestSecurityMiddlewareIntegration:
    """安全中间件集成测试"""

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_security_headers_middleware(self, client):
        """测试安全头中间件"""
        response = await client.get("/health")

        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_sql_injection_protection_middleware(self, client):
        """测试SQL注入防护中间件"""
        # 测试查询参数中的SQL注入
        response = await client.get("/api/v1/stocks", params={"query": "1 OR 1=1"})

        assert response.status_code == 400
        assert "error" in response.json()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_input_validation_middleware(self, client):
        """测试输入验证中间件"""
        # 测试路径遍历攻击
        response = await client.get("/api/v1/stocks/../../../etc/passwd")

        # 应该返回400错误或404（如果路径不存在）
        assert response.status_code in [400, 404]

        # 测试XSS攻击
        response = await client.get("/api/v1/stocks", params={"name": "<script>alert('xss')</script>"})

        assert response.status_code == 400
        assert "error" in response.json()

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_rate_limiting_middleware(self, client):
        """测试限流中间件"""
        # 发送多个请求测试限流
        for i in range(150):  # 超过配置的每分钟100个请求限制
            response = await client.get("/health")
            if response.status_code == 429:
                # 触发限流
                assert "Rate limit exceeded" in response.json()["error"]
                return

        # 如果没有触发限流，说明配置可能有问题
        pytest.fail("Rate limiting did not trigger after 150 requests")
