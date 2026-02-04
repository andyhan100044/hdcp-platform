"""
Security Module
API密钥认证、JWT验证和安全工具
"""
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib
import os

from app.config.settings import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer安全方案
security = HTTPBearer()


class SecurityManager:
    """安全管理器"""

    # 存储API密钥的内存字典 (生产环境应使用数据库或Redis)
    api_keys: dict = {}
    revoked_tokens: set = set()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)

    @staticmethod
    def generate_api_key() -> str:
        """生成API密钥"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """哈希API密钥 (仅存储哈希值)"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @classmethod
    def create_api_key(
        cls,
        name: str,
        user_id: str,
        scopes: List[str] = None,
        expires_in_days: int = 30
    ) -> str:
        """创建API密钥"""
        api_key = cls.generate_api_key()
        api_key_hash = cls.hash_api_key(api_key)

        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        cls.api_keys[api_key_hash] = {
            "name": name,
            "user_id": user_id,
            "scopes": scopes or [],
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "is_active": True
        }

        return api_key

    @classmethod
    def verify_api_key(cls, api_key: str) -> Optional[dict]:
        """验证API密钥"""
        api_key_hash = cls.hash_api_key(api_key)
        key_data = cls.api_keys.get(api_key_hash)

        if not key_data:
            return None

        if not key_data["is_active"]:
            return None

        if datetime.utcnow() > key_data["expires_at"]:
            # 密钥已过期
            key_data["is_active"] = False
            return None

        return key_data

    @classmethod
    def revoke_api_key(cls, api_key: str) -> bool:
        """撤销API密钥"""
        api_key_hash = cls.hash_api_key(api_key)
        if api_key_hash in cls.api_keys:
            cls.api_keys[api_key_hash]["is_active"] = False
            return True
        return False

    @classmethod
    def create_access_token(
        cls,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm="HS256"
        )
        return encoded_jwt

    @classmethod
    def verify_access_token(cls, token: str) -> Optional[dict]:
        """验证访问令牌"""
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=["HS256"]
            )
            return payload
        except JWTError:
            return None

    @classmethod
    def revoke_token(cls, token: str):
        """撤销令牌"""
        cls.revoked_tokens.add(token)

    @classmethod
    def is_token_revoked(cls, token: str) -> bool:
        """检查令牌是否已撤销"""
        return token in cls.revoked_tokens


# 依赖项: 获取当前用户
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """从Bearer令牌获取当前用户"""
    token = credentials.credentials

    # 检查令牌是否已撤销
    if SecurityManager.is_token_revoked(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证令牌
    payload = SecurityManager.verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# 依赖项: 获取当前API密钥用户
async def get_current_api_key_user(
    api_key: str = Security(HTTPBearer())
) -> dict:
    """从API密钥获取当前用户"""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=api_key)

    # 验证API密钥
    user_data = SecurityManager.verify_api_key(credentials.credentials)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_data


# 依赖项: 检查作用域
async def check_scope(
    required_scope: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """检查用户是否有指定作用域"""
    user_scopes = current_user.get("scopes", [])
    if required_scope not in user_scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions (required scope: {required_scope})"
        )
    return current_user


# 工具函数
def generate_secure_token(length: int = 32) -> str:
    """生成安全令牌"""
    return secrets.token_urlsafe(length)


def hash_sensitive_data(data: str, salt: str = None) -> tuple:
    """哈希敏感数据"""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        data.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )
    return hashed.hex(), salt


def verify_sensitive_data(data: str, hashed: str, salt: str) -> bool:
    """验证敏感数据"""
    test_hash, _ = hash_sensitive_data(data, salt)
    return test_hash == hashed


def is_strong_password(password: str) -> tuple:
    """检查密码强度"""
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")

    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")

    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")

    return len(errors) == 0, errors
