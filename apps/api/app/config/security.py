"""
安全配置
Security configuration for HDCP Platform
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
import os


class SecuritySettings(BaseSettings):
    """安全设置"""

    # 认证相关
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # API密钥设置
    API_KEY_HEADER_NAME: str = "X-API-Key"
    API_KEYS_ENABLED: bool = True
    API_KEY_EXPIRE_DAYS: int = 30

    # 密码设置
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # 限流设置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000

    # CSRF保护
    CSRF_PROTECTION_ENABLED: bool = True
    CSRF_TOKEN_EXPIRE_MINUTES: int = 60

    # 跨域资源共享
    CORS_ORIGINS: List[str] = []
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    CORS_HEADERS: List[str] = ["*"]

    # 安全头设置
    SECURITY_HEADERS_ENABLED: bool = True
    CONTENT_SECURITY_POLICY: Optional[str] = None

    # SSL/TLS设置
    SSL_VERIFY: bool = True
    SSL_CA_BUNDLE: Optional[str] = None

    # 会话设置
    SESSION_TIMEOUT_MINUTES: int = 60
    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "strict"

    # 日志设置
    SECURITY_LOGGING_ENABLED: bool = True
    LOG_FAILED_LOGINS: bool = True
    LOG_SUSPICIOUS_ACTIVITIES: bool = True

    class Config:
        env_file = ".env"


class SecurityConfig:
    """安全配置管理器"""

    def __init__(self, settings: SecuritySettings):
        self.settings = settings

    def is_production(self) -> bool:
        """检查是否为生产环境"""
        return os.getenv("ENVIRONMENT", "development") == "production"

    def get_allowed_origins(self) -> List[str]:
        """获取允许的源"""
        if self.settings.CORS_ORIGINS:
            return self.settings.CORS_ORIGINS

        if self.is_production():
            return []  # 生产环境必须明确指定源
        else:
            return ["http://localhost:3000", "http://localhost:1337"]

    def get_cors_settings(self) -> dict:
        """获取CORS设置"""
        return {
            "allow_origins": self.get_allowed_origins(),
            "allow_credentials": self.settings.CORS_CREDENTIALS,
            "allow_methods": self.settings.CORS_METHODS,
            "allow_headers": self.settings.CORS_HEADERS,
        }

    def get_security_headers(self) -> dict:
        """获取安全头设置"""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }

        if self.is_production():
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            headers["Permissions-Policy"] = (
                "camera=(), microphone=(), geolocation=()"
            )

        if self.settings.CONTENT_SECURITY_POLICY:
            headers["Content-Security-Policy"] = self.settings.CONTENT_SECURITY_POLICY

        return headers

    def get_rate_limit_config(self) -> dict:
        """获取限流配置"""
        return {
            "enabled": self.settings.RATE_LIMIT_ENABLED,
            "per_minute": self.settings.RATE_LIMIT_PER_MINUTE,
            "per_hour": self.settings.RATE_LIMIT_PER_HOUR,
            "per_day": self.settings.RATE_LIMIT_PER_DAY,
        }

    def should_log_security_events(self) -> bool:
        """检查是否应记录安全事件"""
        return self.settings.SECURITY_LOGGING_ENABLED

    def is_csrf_protection_enabled(self) -> bool:
        """检查是否启用CSRF保护"""
        return self.settings.CSRF_PROTECTION_ENABLED

    def validate_password_strength(self, password: str) -> tuple:
        """验证密码强度"""
        errors = []

        if len(password) < self.settings.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {self.settings.PASSWORD_MIN_LENGTH} characters long")

        if self.settings.PASSWORD_REQUIRE_UPPERCASE:
            if not any(c.isupper() for c in password):
                errors.append("Password must contain at least one uppercase letter")

        if self.settings.PASSWORD_REQUIRE_LOWERCASE:
            if not any(c.islower() for c in password):
                errors.append("Password must contain at least one lowercase letter")

        if self.settings.PASSWORD_REQUIRE_DIGITS:
            if not any(c.isdigit() for c in password):
                errors.append("Password must contain at least one digit")

        if self.settings.PASSWORD_REQUIRE_SPECIAL:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                errors.append("Password must contain at least one special character")

        return len(errors) == 0, errors

    def get_session_settings(self) -> dict:
        """获取会话设置"""
        return {
            "timeout_minutes": self.settings.SESSION_TIMEOUT_MINUTES,
            "cookie_name": self.settings.SESSION_COOKIE_NAME,
            "cookie_secure": self.settings.SESSION_COOKIE_SECURE and self.is_production(),
            "cookie_httponly": self.settings.SESSION_COOKIE_HTTPONLY,
            "cookie_samesite": self.settings.SESSION_COOKIE_SAMESITE,
        }


# 创建安全配置实例
security_settings = SecuritySettings()
security_config = SecurityConfig(security_settings)
