"""
E2E 測試基礎設施
測試完整 HTTP 請求流程（API → Service → Repository → Database）
"""
import pytest
from typing import AsyncGenerator, Dict
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.auth.password_handler import password_handler


# 使用 SQLite 記憶體資料庫進行測試
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_engine():
    """創建測試資料庫引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # 創建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """創建測試資料庫 session"""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def async_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    創建 HTTP 測試客戶端
    覆蓋應用的資料庫 dependency
    """
    # 覆蓋 get_db dependency
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    # 創建 async HTTP client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    # 清理
    app.dependency_overrides.clear()


# ==================== 認證用戶 Fixtures ====================

@pytest.fixture
async def test_adopter_user(test_db: AsyncSession) -> User:
    """創建測試領養者用戶"""
    user = User(
        email="adopter@test.com",
        password_hash=password_handler.hash_password("TestPass123!"),
        name="Test Adopter",
        phone="0912345678",
        role=UserRole.adopter,
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def test_shelter_user(test_db: AsyncSession) -> User:
    """創建測試收容所用戶"""
    user = User(
        email="shelter@test.com",
        password_hash=password_handler.hash_password("TestPass123!"),
        name="Test Shelter",
        phone="0923456789",
        role=UserRole.shelter,
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def test_admin_user(test_db: AsyncSession) -> User:
    """創建測試管理員用戶"""
    user = User(
        email="admin@test.com",
        password_hash=password_handler.hash_password("TestPass123!"),
        name="Test Admin",
        phone="0934567890",
        role=UserRole.admin,
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def adopter_auth_headers(
    async_client: AsyncClient,
    test_adopter_user: User
) -> Dict[str, str]:
    """
    創建領養者認證 headers
    登入並返回 JWT token headers
    """
    response = await async_client.post(
        "/api/v2/auth/login",
        json={
            "email": "adopter@test.com",
            "password": "TestPass123!"
        }
    )
    assert response.status_code == 200
    tokens = response.json()["tokens"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture
async def shelter_auth_headers(
    async_client: AsyncClient,
    test_shelter_user: User
) -> Dict[str, str]:
    """創建收容所認證 headers"""
    response = await async_client.post(
        "/api/v2/auth/login",
        json={
            "email": "shelter@test.com",
            "password": "TestPass123!"
        }
    )
    assert response.status_code == 200
    tokens = response.json()["tokens"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture
async def admin_auth_headers(
    async_client: AsyncClient,
    test_admin_user: User
) -> Dict[str, str]:
    """創建管理員認證 headers"""
    response = await async_client.post(
        "/api/v2/auth/login",
        json={
            "email": "admin@test.com",
            "password": "TestPass123!"
        }
    )
    assert response.status_code == 200
    tokens = response.json()["tokens"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# ==================== 測試資料 Fixtures ====================

@pytest.fixture
def sample_pet_data() -> Dict:
    """寵物測試資料"""
    return {
        "name": "Lucky",
        "species": "dog",
        "breed": "Golden Retriever",
        "age_years": 2,
        "age_months": 6,
        "gender": "male",
        "size": "large",
        "color": "Golden",
        "description": "Friendly and energetic dog",
        "personality": "Active and loving",
        "medical_history": "All vaccinations up to date",
        "adoption_fee": 200,
        "energy_level": "high",
        "good_with_kids": True,
        "good_with_pets": True,
        "house_trained": True,
        "spayed_neutered": True
    }


@pytest.fixture
def sample_adoption_data() -> Dict:
    """領養申請測試資料"""
    return {
        "experience": "I have raised dogs for 5 years",
        "living_situation": "House with a big yard",
        "household_members": 4,
        "has_other_pets": True,
        "other_pets_description": "One cat and one dog",
        "work_schedule": "9 to 5, Monday to Friday",
        "why_adopt": "Looking for a companion for our family",
        "veterinarian_info": "Dr. Smith at Pet Clinic"
    }
