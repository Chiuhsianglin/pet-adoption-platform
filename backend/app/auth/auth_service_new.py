"""
Authentication Service (Three-Layer Architecture)
使用 Repository 層的認證服務
"""
from datetime import datetime
from typing import Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.password_history import PasswordHistory
from app.repositories.user import UserRepository
from app.repositories.password_history import PasswordHistoryRepository
from app.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
    AccountDeactivatedError,
)
from app.auth.jwt_handler import jwt_handler
from app.auth.password_handler import password_handler
from app.auth.email_service import email_verification_service
import logging

logger = logging.getLogger(__name__)

# Redis-Optional Login Attempt Tracker (保持不變)
try:
    import redis.asyncio as redis
    from app.core.config import settings
    redis_client = redis.from_url(settings.REDIS_URL) if hasattr(settings, 'REDIS_URL') else None
except Exception:
    redis = None
    redis_client = None


class LoginAttemptTracker:
    """Track login attempts and implement rate limiting (Redis optional)"""

    def __init__(self):
        self.max_attempts = 5
        self.lockout_duration_minutes = 30
        self._redis_client: Optional["redis.Redis"] = None

    async def get_redis_client(self) -> Optional["redis.Redis"]:
        """Try to return Redis client, or None if not available."""
        if not redis:
            return None
        try:
            if self._redis_client is None:
                from app.core.config import settings
                self._redis_client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
            await self._redis_client.ping()
            return self._redis_client
        except Exception:
            return None

    async def record_failed_attempt(self, identifier: str) -> None:
        """Record a failed login attempt"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return
        try:
            key = f"login_attempts:{identifier}"
            current_attempts = await redis_client.incr(key)
            if current_attempts == 1:
                await redis_client.expire(key, self.lockout_duration_minutes * 60)
        except Exception:
            pass

    async def clear_failed_attempts(self, identifier: str) -> None:
        """Clear failed login attempts"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return
        try:
            await redis_client.delete(f"login_attempts:{identifier}")
        except Exception:
            pass

    async def is_locked_out(self, identifier: str) -> bool:
        """Check if user is locked out"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return False
        try:
            attempts = await redis_client.get(f"login_attempts:{identifier}")
            return attempts is not None and int(attempts) >= self.max_attempts
        except Exception:
            return False

    async def get_lockout_info(self, identifier: str) -> Dict[str, Any]:
        """Get lockout info"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return {"locked_out": False, "attempts": 0, "remaining_time": 0}
        try:
            key = f"login_attempts:{identifier}"
            attempts = await redis_client.get(key)
            ttl = await redis_client.ttl(key)
            if attempts is None:
                return {"locked_out": False, "attempts": 0, "remaining_time": 0}
            attempts_count = int(attempts)
            locked_out = attempts_count >= self.max_attempts
            return {
                "locked_out": locked_out,
                "attempts": attempts_count,
                "remaining_time": ttl if ttl > 0 else 0,
                "max_attempts": self.max_attempts
            }
        except Exception:
            return {"locked_out": False, "attempts": 0, "remaining_time": 0}


class AuthServiceNew:
    """
    Authentication Service (Three-Layer Architecture)
    使用 Repository 模式的認證服務
    """

    def __init__(
        self,
        user_repo: UserRepository,
        password_history_repo: PasswordHistoryRepository
    ):
        self.user_repo = user_repo
        self.password_history_repo = password_history_repo
        self.login_tracker = LoginAttemptTracker()

    async def register_user(
        self,
        email: str,
        password: str,
        name: str,
        phone: Optional[str] = None,
        role: UserRole = UserRole.adopter
    ) -> Dict[str, Any]:
        """
        註冊新用戶
        
        Args:
            email: 用戶 email
            password: 明文密碼
            name: 用戶姓名
            phone: 電話號碼（可選）
            role: 用戶角色
            
        Returns:
            包含用戶資訊和 tokens 的字典
            
        Raises:
            UserAlreadyExistsError: Email 已存在
            ValueError: 密碼不符合要求
        """
        # 1. 密碼強度驗證
        password_validation = password_handler.validate_password_strength(password)
        if not password_validation["is_valid"]:
            raise ValueError(
                f"Password does not meet requirements: {', '.join(password_validation['errors'])}"
            )

        # 2. 檢查 email 是否已存在（使用 Repository）
        email_lower = email.lower()
        if await self.user_repo.email_exists(email_lower):
            raise UserAlreadyExistsError(f"Email {email} is already registered")

        # 3. 建立新用戶
        hashed_password = password_handler.hash_password(password)
        new_user = User(
            email=email_lower,
            password_hash=hashed_password,
            name=name,
            phone=phone,
            role=role,
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        created_user = await self.user_repo.create(new_user)

        # 4. 建立密碼歷史記錄
        password_history_entry = PasswordHistory(
            user_id=created_user.id,
            password_hash=hashed_password,
            created_at=datetime.utcnow()
        )
        await self.password_history_repo.create(password_history_entry)

        # 5. 發送驗證信（失敗不影響註冊）
        try:
            verification_token = email_verification_service.generate_verification_token(
                created_user.id, created_user.email
            )
            await email_verification_service.store_verification_token(
                created_user.id, verification_token
            )
            await email_verification_service.send_verification_email(
                created_user.email,
                verification_token,
                created_user.name or created_user.email
            )
        except Exception as e:
            logger.warning(f"Failed to send verification email to {email}: {e}")

        # 6. 生成 JWT tokens
        tokens = jwt_handler.create_token_pair(created_user)

        return {
            "user": {
                "id": created_user.id,
                "email": created_user.email,
                "name": created_user.name,
                "role": created_user.role.value,
                "is_active": created_user.is_active,
                "is_verified": created_user.is_verified,
                "phone": created_user.phone,
            },
            "tokens": tokens,
            "message": "Registration successful. Please verify your email address."
        }

    async def login_user(
        self,
        email: str,
        password: str,
        remember_me: bool = False,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        用戶登入
        
        Args:
            email: 用戶 email
            password: 明文密碼
            remember_me: 是否記住登入
            ip_address: 客戶端 IP
            
        Returns:
            包含用戶資訊和 tokens 的字典
            
        Raises:
            InvalidCredentialsError: 密碼錯誤
            UserNotFoundError: 用戶不存在
            AccountDeactivatedError: 帳號已停用
        """
        email_lower = email.lower()
        identifier = f"{email_lower}:{ip_address}" if ip_address else email_lower

        # 1. 檢查登入鎖定
        if await self.login_tracker.is_locked_out(identifier):
            lockout_info = await self.login_tracker.get_lockout_info(identifier)
            raise InvalidCredentialsError(
                f"Too many failed login attempts. Please try again in {lockout_info['remaining_time']} seconds."
            )

        # 2. 透過 Repository 查詢用戶
        user = await self.user_repo.get_by_email(email_lower)
        if not user:
            await self.login_tracker.record_failed_attempt(identifier)
            raise InvalidCredentialsError("Invalid email or password")

        # 3. 驗證密碼
        if not password_handler.verify_password(password, user.password_hash):
            await self.login_tracker.record_failed_attempt(identifier)
            raise InvalidCredentialsError("Invalid email or password")

        # 4. 檢查帳號狀態
        if not user.is_active:
            raise AccountDeactivatedError("Your account has been deactivated")

        # 5. 清除失敗記錄
        await self.login_tracker.clear_failed_attempts(identifier)

        # 6. 更新最後登入時間
        await self.user_repo.update_last_login(user.id)

        # 7. 生成 tokens
        tokens = jwt_handler.create_token_pair(user)

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role.value,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "phone": user.phone,
            },
            "tokens": tokens,
            "message": "Login successful"
        }

    async def logout_user(
        self,
        access_token: str,
        refresh_token: Optional[str] = None
    ) -> Dict[str, str]:
        """
        用戶登出（將 token 加入黑名單）
        
        Args:
            access_token: 存取 token
            refresh_token: 刷新 token（可選）
            
        Returns:
            成功訊息
        """
        try:
            # 若有 Redis，將 token 加入黑名單
            redis_client_instance = await self.login_tracker.get_redis_client()
            if redis_client_instance:
                await redis_client_instance.setex(
                    f"blacklist:{access_token}",
                    3600,  # 1 hour
                    "1"
                )
                if refresh_token:
                    await redis_client_instance.setex(
                        f"blacklist:{refresh_token}",
                        7 * 24 * 3600,  # 7 days
                        "1"
                    )
            
            return {"message": "Logout successful"}
        except Exception as e:
            logger.warning(f"Logout error: {e}")
            return {"message": "Logout successful"}

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        刷新 access token
        
        Args:
            refresh_token: 刷新 token
            
        Returns:
            新的 token pair
            
        Raises:
            InvalidCredentialsError: Token 無效
        """
        try:
            # 1. 解析 refresh token
            payload = jwt_handler.decode_token(refresh_token)
            user_id = payload.get("user_id") or payload.get("sub")
            
            if not user_id:
                raise InvalidCredentialsError("Invalid token")

            # 2. 檢查黑名單
            redis_client_instance = await self.login_tracker.get_redis_client()
            if redis_client_instance:
                blacklisted = await redis_client_instance.get(f"blacklist:{refresh_token}")
                if blacklisted:
                    raise InvalidCredentialsError("Token has been revoked")

            # 3. 透過 Repository 查詢用戶
            user = await self.user_repo.get_by_id(int(user_id))
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")

            if not user.is_active:
                raise AccountDeactivatedError("Account is deactivated")

            # 4. 生成新的 token pair
            tokens = jwt_handler.create_token_pair(user)
            
            return tokens

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise InvalidCredentialsError("Token refresh failed")

    async def get_user_by_token(self, token: str) -> User:
        """
        通過 token 獲取用戶
        
        Args:
            token: JWT access token
            
        Returns:
            User 對象
            
        Raises:
            InvalidCredentialsError: Token 無效
            UserNotFoundError: 用戶不存在
        """
        try:
            # 1. 解析 token
            payload = jwt_handler.decode_token(token)
            user_id = payload.get("user_id") or payload.get("sub")
            
            if not user_id:
                raise InvalidCredentialsError("Invalid token payload")

            # 2. 檢查黑名單（Redis 可選）
            redis_client_instance = await self.login_tracker.get_redis_client()
            if redis_client_instance:
                try:
                    blacklisted = await redis_client_instance.get(f"blacklist:{token}")
                    if blacklisted:
                        raise InvalidCredentialsError("Token has been revoked")
                except Exception as e:
                    logger.warning(f"Redis check failed: {e}")

            # 3. 透過 Repository 查詢用戶
            user = await self.user_repo.get_by_id(int(user_id))
            if not user:
                raise UserNotFoundError(f"User {user_id} not found")

            return user

        except InvalidCredentialsError:
            raise
        except UserNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise InvalidCredentialsError("Token verification failed")

    async def verify_email(self, user_id: int, token: str) -> Dict[str, Any]:
        """
        驗證用戶 email
        
        Args:
            user_id: 用戶 ID
            token: 驗證 token
            
        Returns:
            成功訊息
            
        Raises:
            UserNotFoundError: 用戶不存在
            InvalidCredentialsError: Token 無效
        """
        # 1. 驗證 token
        is_valid = await email_verification_service.verify_token(user_id, token)
        if not is_valid:
            raise InvalidCredentialsError("Invalid or expired verification token")

        # 2. 透過 Repository 更新用戶
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        user.is_verified = True
        user.updated_at = datetime.utcnow()
        await self.user_repo.update(user)

        # 3. 刪除驗證 token
        await email_verification_service.delete_verification_token(user_id)

        return {
            "message": "Email verified successfully",
            "user_id": user_id
        }

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> Dict[str, str]:
        """
        修改密碼
        
        Args:
            user_id: 用戶 ID
            current_password: 當前密碼
            new_password: 新密碼
            
        Returns:
            成功訊息
            
        Raises:
            UserNotFoundError: 用戶不存在
            InvalidCredentialsError: 當前密碼錯誤
            ValueError: 新密碼不符合要求
        """
        # 1. 驗證新密碼強度
        password_validation = password_handler.validate_password_strength(new_password)
        if not password_validation["is_valid"]:
            raise ValueError(
                f"New password does not meet requirements: {', '.join(password_validation['errors'])}"
            )

        # 2. 獲取用戶
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        # 3. 驗證當前密碼
        if not password_handler.verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect")

        # 4. 檢查新密碼是否與歷史密碼重複
        recent_passwords = await self.password_history_repo.get_recent_passwords(user_id, limit=5)
        for history in recent_passwords:
            if password_handler.verify_password(new_password, history.password_hash):
                raise ValueError("Cannot reuse recent passwords")

        # 5. 更新密碼
        new_hash = password_handler.hash_password(new_password)
        user.password_hash = new_hash
        user.updated_at = datetime.utcnow()
        await self.user_repo.update(user)

        # 6. 記錄密碼歷史
        password_history_entry = PasswordHistory(
            user_id=user_id,
            password_hash=new_hash,
            created_at=datetime.utcnow()
        )
        await self.password_history_repo.create(password_history_entry)

        return {"message": "Password changed successfully"}
