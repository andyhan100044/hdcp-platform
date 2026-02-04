"""
Security Middleware
安全中间件 - 添加安全头、防护攻击等
"""
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import secrets
import hashlib
import os
import re


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        # 添加CSP头 (仅生产环境)
        if os.getenv("ENVIRONMENT", "development") == "production":
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self' https://api.example.com;"
            )
            response.headers["Content-Security-Policy"] = csp

        return response


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF保护中间件"""

    # 存储CSRF令牌的内存字典 (生产环境应使用Redis)
    csrf_tokens: dict = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 只对POST、PUT、DELETE请求检查CSRF
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # 检查是否跳过CSRF验证的路径
            skip_paths = [
                "/api/webhooks",
                "/api/auth/login",
                "/api/auth/register"
            ]

            if not any(request.url.path.startswith(path) for path in skip_paths):
                # 检查CSRF令牌
                csrf_token = request.headers.get("X-CSRF-Token")

                if not csrf_token:
                    return Response(
                        content='{"error": "CSRF token missing"}',
                        status_code=403,
                        headers={"Content-Type": "application/json"}
                    )

                # 验证CSRF令牌
                session_id = request.cookies.get("session_id")
                if session_id not in self.csrf_tokens:
                    return Response(
                        content='{"error": "Invalid CSRF token"}',
                        status_code=403,
                        headers={"Content-Type": "application/json"}
                    )

                stored_token = self.csrf_tokens.get(session_id)
                if stored_token != csrf_token:
                    return Response(
                        content='{"error": "CSRF token mismatch"}',
                        status_code=403,
                        headers={"Content-Type": "application/json"}
                    )

        response = await call_next(request)

        # 为表单页面生成CSRF令牌
        if request.method == "GET" and "text/html" in request.headers.get("accept", ""):
            session_id = request.cookies.get("session_id")
            if session_id:
                csrf_token = secrets.token_urlsafe(32)
                self.csrf_tokens[session_id] = csrf_token
                response.headers["X-CSRF-Token"] = csrf_token

        return response

    @classmethod
    def generate_csrf_token(cls, session_id: str) -> str:
        """生成CSRF令牌"""
        token = secrets.token_urlsafe(32)
        cls.csrf_tokens[session_id] = token
        return token


class SQLInjectionProtectionMiddleware(BaseHTTPMiddleware):
    """SQL注入防护中间件"""

    # SQL注入关键字模式
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b\s+select\b)",
        r"(\bdrop\b\s+(table|database)\b)",
        r"(\bdelete\b\s+from\b)",
        r"(\binsert\b\s+into\b)",
        r"(\bupdate\b\s+set\b)",
        r"(\balter\b\s+table\b)",
        r"(\bcreate\b\s+(table|database)\b)",
        r"(\bexec\b)",
        r"(\bexecute\b)",
        r"('|\bor\b|\b1=1\b)",
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查请求参数中的SQL注入模式
        if request.method in ["POST", "PUT", "GET"]:
            # 检查查询参数
            for key, value in request.query_params.items():
                if self._contains_sql_injection(str(value)):
                    return Response(
                        content='{"error": "Potential SQL injection detected"}',
                        status_code=400,
                        headers={"Content-Type": "application/json"}
                    )

            # 检查表单数据
            try:
                body = await request.body()
                if body:
                    body_str = body.decode("utf-8")
                    if self._contains_sql_injection(body_str):
                        return Response(
                            content='{"error": "Potential SQL injection detected"}',
                            status_code=400,
                            headers={"Content-Type": "application/json"}
                        )
            except:
                pass  # 忽略解码错误

        response = await call_next(request)
        return response

    def _contains_sql_injection(self, text: str) -> bool:
        """检查文本是否包含SQL注入模式"""
        text_lower = text.lower()
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False


class RateLimitByUserMiddleware(BaseHTTPMiddleware):
    """基于用户的限流中间件"""

    import time

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.user_requests = {}  # {user_id: [timestamp1, timestamp2, ...]}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取用户标识符
        user_id = self._get_user_identifier(request)

        if user_id:
            current_time = time.time()

            # 清理过期记录
            if user_id in self.user_requests:
                self.user_requests[user_id] = [
                    t for t in self.user_requests[user_id]
                    if current_time - t < 60  # 保留最近60秒的记录
                ]
            else:
                self.user_requests[user_id] = []

            # 检查请求数量
            if len(self.user_requests[user_id]) >= self.requests_per_minute:
                return Response(
                    content='{"error": "Rate limit exceeded"}',
                    status_code=429,
                    headers={
                        "Content-Type": "application/json",
                        "X-RateLimit-Limit": str(self.requests_per_minute),
                        "X-RateLimit-Remaining": "0"
                    }
                )

            # 记录请求
            self.user_requests[user_id].append(current_time)

        response = await call_next(request)
        return response

    def _get_user_identifier(self, request: Request) -> Optional[str]:
        """获取用户标识符"""
        # 优先使用API密钥
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return f"api_key:{auth_header[7:]}"

        # 使用IP地址
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        return f"ip:{client_ip}"


class InputValidationMiddleware(BaseHTTPMiddleware):
    """输入验证中间件"""

    import re

    # XSS模式
    XSS_PATTERNS = [
        r"<script.*?>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe.*?>.*?</iframe>",
        r"<object.*?>.*?</object>",
        r"<embed.*?>.*?</embed>",
    ]

    # 路径遍历模式
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e%5c",
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查路径
        if self._contains_malicious_pattern(request.url.path, self.PATH_TRAVERSAL_PATTERNS):
            return Response(
                content='{"error": "Invalid path"}',
                status_code=400,
                headers={"Content-Type": "application/json"}
            )

        # 检查查询参数
        for key, value in request.query_params.items():
            if self._contains_malicious_pattern(str(value), self.XSS_PATTERNS + self.PATH_TRAVERSAL_PATTERNS):
                return Response(
                    content='{"error": "Malicious input detected"}',
                    status_code=400,
                    headers={"Content-Type": "application/json"}
                )

        response = await call_next(request)
        return response

    def _contains_malicious_pattern(self, text: str, patterns: list) -> bool:
        """检查文本是否包含恶意模式"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
