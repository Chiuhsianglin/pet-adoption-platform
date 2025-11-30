"""
測試新架構的基本功能
驗證 Repository 和 Service 層是否正常工作
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 假設使用測試資料庫
DATABASE_URL = "sqlite+aiosqlite:///:memory:"


async def test_imports():
    """測試所有模組是否能正常導入"""
    print("📦 測試模組導入...")
    
    try:
        from app.repositories import (
            AdoptionRepository,
            PetRepository,
            NotificationRepository,
            UserRepository,
            ChatRepository,
            MessageRepository,
            CommunityRepository,
        )
        print("✅ Repository 模組導入成功")
        
        from app.services.factories import (
            AdoptionServiceFactory,
            PetServiceFactory,
            NotificationServiceFactory,
            ChatServiceFactory,
            CommunityServiceFactory,
        )
        print("✅ Service Factory 模組導入成功")
        
        from app.services.adoption_service_new import AdoptionService
        from app.services.pet_service_new import PetService
        from app.services.notification_service_new import NotificationService
        from app.services.chat_service_new import ChatService
        from app.services.community_service_new import CommunityService
        print("✅ Service 模組導入成功")
        
        from app.exceptions import (
            ApplicationNotFoundError,
            PetNotFoundError,
            PermissionDeniedError,
            BusinessException,
        )
        print("✅ Exception 模組導入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 導入失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_repository_instantiation():
    """測試 Repository 能否正常實例化"""
    print("\n🏗️  測試 Repository 實例化...")
    
    try:
        from app.repositories import AdoptionRepository, PetRepository
        from sqlalchemy.ext.asyncio import AsyncSession
        from unittest.mock import Mock
        
        # 創建 mock session
        mock_session = Mock(spec=AsyncSession)
        
        # 實例化 Repository
        adoption_repo = AdoptionRepository(mock_session)
        pet_repo = PetRepository(mock_session)
        
        print("✅ Repository 實例化成功")
        return True
        
    except Exception as e:
        print(f"❌ 實例化失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_service_factory():
    """測試 Service Factory 能否正常創建 Service"""
    print("\n🏭 測試 Service Factory...")
    
    try:
        from app.services.factories import (
            AdoptionServiceFactory,
            PetServiceFactory,
            NotificationServiceFactory,
        )
        from unittest.mock import Mock
        from sqlalchemy.ext.asyncio import AsyncSession
        
        # 創建 mock session
        mock_session = Mock(spec=AsyncSession)
        
        # 使用 Factory 創建 Service
        adoption_service = AdoptionServiceFactory.create(mock_session)
        pet_service = PetServiceFactory.create(mock_session)
        notification_service = NotificationServiceFactory.create(mock_session)
        
        print("✅ Service Factory 創建成功")
        print(f"   - AdoptionService: {type(adoption_service).__name__}")
        print(f"   - PetService: {type(pet_service).__name__}")
        print(f"   - NotificationService: {type(notification_service).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service Factory 失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_exception_hierarchy():
    """測試例外類別繼承關係"""
    print("\n⚠️  測試例外類別...")
    
    try:
        from app.exceptions import (
            BusinessException,
            ApplicationNotFoundError,
            PetNotFoundError,
            PermissionDeniedError,
            InvalidStatusTransitionError,
        )
        
        # 測試繼承關係
        assert issubclass(ApplicationNotFoundError, BusinessException)
        assert issubclass(PetNotFoundError, BusinessException)
        assert issubclass(PermissionDeniedError, BusinessException)
        assert issubclass(InvalidStatusTransitionError, BusinessException)
        
        # 測試例外創建
        exc = ApplicationNotFoundError("測試訊息")
        assert str(exc) == "測試訊息"
        
        print("✅ 例外類別正常")
        return True
        
    except Exception as e:
        print(f"❌ 例外測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """執行所有測試"""
    print("=" * 60)
    print("🧪 三層架構測試套件")
    print("=" * 60)
    
    results = []
    
    # 執行測試
    results.append(("模組導入", await test_imports()))
    results.append(("Repository 實例化", await test_repository_instantiation()))
    results.append(("Service Factory", await test_service_factory()))
    results.append(("例外類別", await test_exception_hierarchy()))
    
    # 總結
    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n通過率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有測試通過！新架構基礎功能正常。")
        return True
    else:
        print("\n⚠️  部分測試失敗，需要修復。")
        return False


if __name__ == "__main__":
    asyncio.run(main())
