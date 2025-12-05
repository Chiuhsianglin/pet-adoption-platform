"""
Auth API E2E 測試
測試完整認證流程：HTTP Request → Controller → Service → Repository → Database
"""
import pytest
from httpx import AsyncClient
from app.models.user import User


# ==================== 註冊測試 ====================

@pytest.mark.asyncio
class TestRegisterAPI:
    """測試用戶註冊 API"""
    
    async def test_register_adopter_success(self, async_client: AsyncClient):
        """測試成功註冊領養者"""
        response = await async_client.post(
            "/api/v2/auth/register",
            json={
                "email": "newadopter@test.com",
                "password": "SecurePass123!",
                "name": "New Adopter",
                "phone": "0987654321",
                "role": "adopter"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert "tokens" in data
        user = data["user"]
        assert user["email"] == "newadopter@test.com"
        assert user["name"] == "New Adopter"
        assert user["role"] == "adopter"
        assert user["is_active"] is True
        assert "password" not in user
        assert "password_hash" not in user
    
    async def test_register_shelter_success(self, async_client: AsyncClient):
        """測試成功註冊收容所"""
        response = await async_client.post(
            "/api/v2/auth/register",
            json={
                "email": "newshelter@test.com",
                "password": "SecurePass123!",
                "name": "New Shelter",
                "phone": "0976543210",
                "role": "shelter"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["role"] == "shelter"
    
    async def test_register_duplicate_email(
        self,
        async_client: AsyncClient,
        test_adopter_user: User
    ):
        """測試註冊重複 email"""
        response = await async_client.post(
            "/api/v2/auth/register",
            json={
                "email": "adopter@test.com",  # 已存在
                "password": "SecurePass123!",
                "name": "Duplicate User",
                "phone": "0987654321",
                "role": "adopter"
            }
        )
        
        assert response.status_code == 400
        error_detail = response.json()["detail"].lower()
        assert "email" in error_detail and "already registered" in error_detail
    
    async def test_register_weak_password(self, async_client: AsyncClient):
        """測試弱密碼註冊"""
        response = await async_client.post(
            "/api/v2/auth/register",
            json={
                "email": "weakpass@test.com",
                "password": "weak",  # 太弱
                "name": "Weak Password User",
                "phone": "0987654321",
                "role": "adopter"
            }
        )
        
        assert response.status_code in [400, 422]
        # 422 for Pydantic validation error
        if response.status_code == 422:
            # Pydantic validation error format
            assert "detail" in response.json()
        else:
            error_detail = response.json()["detail"].lower()
            assert any(word in error_detail for word in ["password", "weak", "invalid"])
    
    async def test_register_missing_fields(self, async_client: AsyncClient):
        """測試缺少必填欄位"""
        response = await async_client.post(
            "/api/v2/auth/register",
            json={
                "email": "incomplete@test.com",
                "password": "SecurePass123!"
                # 缺少 name, phone, role
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    async def test_register_invalid_email(self, async_client: AsyncClient):
        """測試無效 email 格式"""
        response = await async_client.post(
            "/api/v2/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePass123!",
                "name": "Invalid Email User",
                "phone": "0987654321",
                "role": "adopter"
            }
        )
        
        assert response.status_code == 422


# ==================== 登入測試 ====================

@pytest.mark.asyncio
class TestLoginAPI:
    """測試用戶登入 API"""
    
    async def test_login_success(
        self,
        async_client: AsyncClient,
        test_adopter_user: User
    ):
        """測試成功登入"""
        response = await async_client.post(
            "/api/v2/auth/login",
            json={
                "email": "adopter@test.com",
                "password": "TestPass123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tokens" in data
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
        assert data["tokens"]["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "adopter@test.com"
    
    async def test_login_wrong_password(
        self,
        async_client: AsyncClient,
        test_adopter_user: User
    ):
        """測試錯誤密碼"""
        response = await async_client.post(
            "/api/v2/auth/login",
            json={
                "email": "adopter@test.com",
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401
        error_detail = response.json()["detail"].lower()
        assert any(word in error_detail for word in ["incorrect", "invalid"])
    
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """測試不存在的用戶"""
        response = await async_client.post(
            "/api/v2/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "TestPass123!"
            }
        )
        
        assert response.status_code == 401
    
    async def test_login_inactive_account(
        self,
        async_client: AsyncClient,
        test_adopter_user: User,
        test_db
    ):
        """測試停用帳號登入"""
        # 停用帳號
        test_adopter_user.is_active = False
        await test_db.commit()
        
        response = await async_client.post(
            "/api/v2/auth/login",
            json={
                "email": "adopter@test.com",
                "password": "TestPass123!"
            }
        )
        
        assert response.status_code in [401, 403]
        error_detail = response.json()["detail"].lower()
        assert any(word in error_detail for word in ["inactive", "deactivated", "forbidden"])


# ==================== Token 管理測試 ====================

@pytest.mark.asyncio
class TestTokenAPI:
    """測試 Token 管理 API"""
    
    async def test_refresh_token_success(
        self,
        async_client: AsyncClient,
        test_adopter_user: User
    ):
        """測試成功刷新 token"""
        # 先登入取得 refresh token
        login_response = await async_client.post(
            "/api/v2/auth/login",
            json={
                "email": "adopter@test.com",
                "password": "TestPass123!"
            }
        )
        refresh_token = login_response.json()["tokens"]["refresh_token"]
        
        # 刷新 token
        response = await async_client.post(
            "/api/v2/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_refresh_token_invalid(self, async_client: AsyncClient):
        """測試無效 refresh token"""
        response = await async_client.post(
            "/api/v2/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )
        
        assert response.status_code == 401
    
    async def test_logout_success(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict
    ):
        """測試成功登出"""
        response = await async_client.post(
            "/api/v2/auth/logout",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()


# ==================== 密碼管理測試 ====================

@pytest.mark.asyncio
class TestPasswordAPI:
    """測試密碼管理 API"""
    
    async def test_change_password_success(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict
    ):
        """測試成功修改密碼"""
        response = await async_client.post(
            "/api/v2/auth/change-password",
            headers=adopter_auth_headers,
            json={
                "current_password": "TestPass123!",
                "new_password": "NewSecurePass456!"
            }
        )
        
        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()
        
        # 驗證可用新密碼登入
        login_response = await async_client.post(
            "/api/v2/auth/login",
            json={
                "email": "adopter@test.com",
                "password": "NewSecurePass456!"
            }
        )
        assert login_response.status_code == 200
    
    async def test_change_password_wrong_current(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict
    ):
        """測試錯誤的當前密碼"""
        response = await async_client.post(
            "/api/v2/auth/change-password",
            headers=adopter_auth_headers,
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewSecurePass456!"
            }
        )
        
        assert response.status_code == 401
        error_detail = response.json()["detail"].lower()
        assert any(word in error_detail for word in ["incorrect", "invalid"])
    
    async def test_change_password_unauthenticated(
        self,
        async_client: AsyncClient
    ):
        """測試未認證修改密碼"""
        response = await async_client.post(
            "/api/v2/auth/change-password",
            json={
                "current_password": "TestPass123!",
                "new_password": "NewSecurePass456!"
            }
        )
        
        assert response.status_code in [401, 403]


# ==================== 用戶資訊測試 ====================

@pytest.mark.asyncio
class TestUserInfoAPI:
    """測試用戶資訊 API"""
    
    async def test_get_current_user_success(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict
    ):
        """測試成功取得當前用戶資訊"""
        response = await async_client.get(
            "/api/v2/auth/me",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "adopter@test.com"
        assert data["name"] == "Test Adopter"
        assert data["role"] == "adopter"
        assert "password" not in data
        assert "password_hash" not in data
    
    async def test_get_current_user_unauthenticated(
        self,
        async_client: AsyncClient
    ):
        """測試未認證取得用戶資訊"""
        response = await async_client.get("/api/v2/auth/me")
        
        assert response.status_code in [401, 403]


# ==================== 角色測試 ====================

@pytest.mark.asyncio
class TestRoleBasedAccess:
    """測試基於角色的存取控制"""
    
    async def test_adopter_role_access(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict
    ):
        """測試領養者角色存取"""
        response = await async_client.get(
            "/api/v2/auth/me",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["role"] == "adopter"
    
    async def test_shelter_role_access(
        self,
        async_client: AsyncClient,
        shelter_auth_headers: dict
    ):
        """測試收容所角色存取"""
        response = await async_client.get(
            "/api/v2/auth/me",
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["role"] == "shelter"
    
    async def test_admin_role_access(
        self,
        async_client: AsyncClient,
        admin_auth_headers: dict
    ):
        """測試管理員角色存取"""
        response = await async_client.get(
            "/api/v2/auth/me",
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["role"] == "admin"
