"""
Authentication Service Factory
認證服務工廠
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import UserRepository
from app.repositories.password_history import PasswordHistoryRepository
from app.auth.auth_service import AuthService


class AuthServiceFactory:
    """
    AuthService Factory
    負責創建 AuthService 實例及其依賴
    """
    
    @staticmethod
    def create(db: AsyncSession) -> AuthService:
        """
        創建 AuthService 實例
        
        Args:
            db: 資料庫 session
            
        Returns:
            AuthService 實例
        """
        # 創建 Repository 實例
        user_repo = UserRepository(db)
        password_history_repo = PasswordHistoryRepository(db)
        
        # 創建並返回 Service 實例
        return AuthService(
            user_repo=user_repo,
            password_history_repo=password_history_repo
        )
