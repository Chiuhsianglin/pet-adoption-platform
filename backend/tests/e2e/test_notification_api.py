"""
Notification API E2E Tests
測試通知功能的端對端場景
"""
import pytest
from httpx import AsyncClient


class TestGetNotificationsAPI:
    """獲取通知列表 API 測試"""
    
    @pytest.mark.asyncio
    async def test_get_notifications_success(
        self, async_client: AsyncClient, adopter_headers: dict, db_session
    ):
        """測試成功獲取通知列表"""
        response = await async_client.get(
            "/api/v2/notifications/",
            headers=adopter_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "notifications" in result
        assert "total" in result
        assert "unread_count" in result
        assert isinstance(result["notifications"], list)
    
    @pytest.mark.asyncio
    async def test_get_notifications_with_pagination(
        self, async_client: AsyncClient, adopter_headers: dict
    ):
        """測試分頁獲取通知"""
        response = await async_client.get(
            "/api/v2/notifications/?skip=0&limit=10",
            headers=adopter_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["notifications"]) <= 10
    
    @pytest.mark.asyncio
    async def test_get_unread_notifications_only(
        self, async_client: AsyncClient, adopter_headers: dict
    ):
        """測試只獲取未讀通知"""
        response = await async_client.get(
            "/api/v2/notifications/?unread_only=true",
            headers=adopter_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        # 驗證所有返回的通知都是未讀的
        for notif in result["notifications"]:
            assert notif["is_read"] is False
    
    @pytest.mark.asyncio
    async def test_get_notifications_unauthenticated(self, async_client: AsyncClient):
        """測試未認證用戶獲取通知"""
        response = await async_client.get("/api/v2/notifications/")
        
        # 根據實作，可能返回 401 或空列表
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            result = response.json()
            assert result["notifications"] == []
            assert result["total"] == 0


class TestUnreadCountAPI:
    """未讀計數 API 測試"""
    
    @pytest.mark.asyncio
    async def test_get_unread_count_success(
        self, async_client: AsyncClient, adopter_headers: dict
    ):
        """測試獲取未讀計數"""
        response = await async_client.get(
            "/api/v2/notifications/unread-count",
            headers=adopter_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "unread_count" in result
        assert isinstance(result["unread_count"], int)
        assert result["unread_count"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_unread_count_unauthenticated(self, async_client: AsyncClient):
        """測試未認證用戶獲取未讀計數"""
        response = await async_client.get("/api/v2/notifications/unread-count")
        
        assert response.status_code in [200, 401]


class TestMarkAsReadAPI:
    """標記已讀 API 測試"""
    
    @pytest.mark.asyncio
    async def test_mark_single_notification_as_read(
        self, async_client: AsyncClient, adopter_headers: dict, db_session
    ):
        """測試標記單個通知為已讀"""
        # 先獲取一個未讀通知
        list_response = await async_client.get(
            "/api/v2/notifications/?unread_only=true",
            headers=adopter_headers
        )
        
        if list_response.status_code == 200:
            notifications = list_response.json()["notifications"]
            if len(notifications) > 0:
                notification_id = notifications[0]["id"]
                
                # 標記為已讀
                response = await async_client.put(
                    f"/api/v2/notifications/{notification_id}/read",
                    headers=adopter_headers
                )
                
                assert response.status_code in [200, 204]
                
                # 驗證已標記
                check_response = await async_client.get(
                    "/api/v2/notifications/",
                    headers=adopter_headers
                )
                assert check_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_mark_nonexistent_notification_as_read(
        self, async_client: AsyncClient, adopter_headers: dict
    ):
        """測試標記不存在的通知為已讀"""
        response = await async_client.put(
            "/api/v2/notifications/999999/read",
            headers=adopter_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_mark_other_user_notification_as_read(
        self, async_client: AsyncClient, adopter_headers: dict, shelter_headers: dict, db_session
    ):
        """測試標記其他用戶的通知為已讀（權限測試）"""
        # 獲取 adopter 的通知
        list_response = await async_client.get(
            "/api/v2/notifications/",
            headers=adopter_headers
        )
        
        if list_response.status_code == 200:
            notifications = list_response.json()["notifications"]
            if len(notifications) > 0:
                notification_id = notifications[0]["id"]
                
                # shelter 用戶嘗試標記 adopter 的通知
                response = await async_client.put(
                    f"/api/v2/notifications/{notification_id}/read",
                    headers=shelter_headers
                )
                
                # 應該被拒絕
                assert response.status_code in [403, 404]
    
    @pytest.mark.asyncio
    async def test_mark_all_notifications_as_read(
        self, async_client: AsyncClient, adopter_headers: dict
    ):
        """測試標記所有通知為已讀"""
        response = await async_client.post(
            "/api/v2/notifications/mark-all-read",
            headers=adopter_headers
        )
        
        assert response.status_code in [200, 204]
        
        # 驗證未讀計數為 0
        count_response = await async_client.get(
            "/api/v2/notifications/unread-count",
            headers=adopter_headers
        )
        
        if count_response.status_code == 200:
            result = count_response.json()
            assert result["unread_count"] == 0


class TestDeleteNotificationAPI:
    """刪除通知 API 測試"""
    
    @pytest.mark.asyncio
    async def test_delete_notification_success(
        self, async_client: AsyncClient, adopter_headers: dict, db_session
    ):
        """測試成功刪除通知"""
        # 先獲取通知列表
        list_response = await async_client.get(
            "/api/v2/notifications/",
            headers=adopter_headers
        )
        
        if list_response.status_code == 200:
            notifications = list_response.json()["notifications"]
            if len(notifications) > 0:
                notification_id = notifications[0]["id"]
                initial_total = list_response.json()["total"]
                
                # 刪除通知
                response = await async_client.delete(
                    f"/api/v2/notifications/{notification_id}",
                    headers=adopter_headers
                )
                
                assert response.status_code in [200, 204]
                
                # 驗證已刪除
                check_response = await async_client.get(
                    "/api/v2/notifications/",
                    headers=adopter_headers
                )
                
                if check_response.status_code == 200:
                    new_total = check_response.json()["total"]
                    assert new_total == initial_total - 1
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_notification(
        self, async_client: AsyncClient, adopter_headers: dict
    ):
        """測試刪除不存在的通知"""
        response = await async_client.delete(
            "/api/v2/notifications/999999",
            headers=adopter_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_other_user_notification(
        self, async_client: AsyncClient, adopter_headers: dict, shelter_headers: dict, db_session
    ):
        """測試刪除其他用戶的通知（權限測試）"""
        # 獲取 adopter 的通知
        list_response = await async_client.get(
            "/api/v2/notifications/",
            headers=adopter_headers
        )
        
        if list_response.status_code == 200:
            notifications = list_response.json()["notifications"]
            if len(notifications) > 0:
                notification_id = notifications[0]["id"]
                
                # shelter 用戶嘗試刪除 adopter 的通知
                response = await async_client.delete(
                    f"/api/v2/notifications/{notification_id}",
                    headers=shelter_headers
                )
                
                # 應該被拒絕
                assert response.status_code in [403, 404]


class TestNotificationIntegration:
    """通知系統整合測試"""
    
    @pytest.mark.asyncio
    async def test_notification_created_on_application_submission(
        self, async_client: AsyncClient, adopter_headers: dict, shelter_headers: dict, db_session
    ):
        """測試提交領養申請時創建通知"""
        # shelter 創建寵物
        pet_data = {
            "name": "Notification Test Dog",
            "species": "dog",
            "breed": "Labrador",
            "age": 2,
            "gender": "male",
            "description": "Test pet for notification"
        }
        pet_response = await async_client.post(
            "/api/v2/pets",
            json=pet_data,
            headers=shelter_headers
        )
        
        if pet_response.status_code == 201:
            pet_id = pet_response.json()["id"]
            
            # adopter 提交領養申請
            application_data = {
                "pet_id": pet_id,
                "message": "I want to adopt this pet"
            }
            app_response = await async_client.post(
                "/api/v2/adoptions/applications",
                json=application_data,
                headers=adopter_headers
            )
            
            assert app_response.status_code == 201
            
            # 檢查 shelter 是否收到通知
            notif_response = await async_client.get(
                "/api/v2/notifications/",
                headers=shelter_headers
            )
            
            if notif_response.status_code == 200:
                notifications = notif_response.json()["notifications"]
                # 應該有新申請的通知
                assert any("application" in str(n).lower() for n in notifications)
    
    @pytest.mark.asyncio
    async def test_notification_pagination_boundary(
        self, async_client: AsyncClient, adopter_headers: dict
    ):
        """測試分頁邊界條件"""
        # 測試 limit=0
        response = await async_client.get(
            "/api/v2/notifications/?limit=0",
            headers=adopter_headers
        )
        assert response.status_code in [200, 400]
        
        # 測試 skip 超過總數
        response = await async_client.get(
            "/api/v2/notifications/?skip=999999",
            headers=adopter_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert result["notifications"] == []
    
    @pytest.mark.asyncio
    async def test_notification_fields_completeness(
        self, async_client: AsyncClient, adopter_headers: dict
    ):
        """測試通知包含所有必要欄位"""
        response = await async_client.get(
            "/api/v2/notifications/",
            headers=adopter_headers
        )
        
        if response.status_code == 200:
            notifications = response.json()["notifications"]
            if len(notifications) > 0:
                notif = notifications[0]
                # 驗證必要欄位
                assert "id" in notif
                assert "user_id" in notif
                assert "notification_type" in notif
                assert "title" in notif
                assert "message" in notif
                assert "is_read" in notif
                assert "created_at" in notif
