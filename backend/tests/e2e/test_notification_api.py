"""
Notification API E2E Tests
æ¸¬è©¦?šçŸ¥?Ÿèƒ½?„ç«¯å°ç«¯?´æ™¯
"""
import pytest
from httpx import AsyncClient


class TestGetNotificationsAPI:
    """?²å??šçŸ¥?—è¡¨ API æ¸¬è©¦"""
    
    @pytest.mark.asyncio
    async def test_get_notifications_success(
        self, async_client: AsyncClient, adopter_auth_headers: dict, db_session
    ):
        """æ¸¬è©¦?å??²å??šçŸ¥?—è¡¨"""
        response = await async_client.get(
            "/api/v2/notifications/",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "notifications" in result
        assert "total" in result
        assert "unread_count" in result
        assert isinstance(result["notifications"], list)
    
    @pytest.mark.asyncio
    async def test_get_notifications_with_pagination(
        self, async_client: AsyncClient, adopter_auth_headers: dict
    ):
        """æ¸¬è©¦?†é??²å??šçŸ¥"""
        response = await async_client.get(
            "/api/v2/notifications/?skip=0&limit=10",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["notifications"]) <= 10
    
    @pytest.mark.asyncio
    async def test_get_unread_notifications_only(
        self, async_client: AsyncClient, adopter_auth_headers: dict
    ):
        """æ¸¬è©¦?ªç²?–æœªè®€?šçŸ¥"""
        response = await async_client.get(
            "/api/v2/notifications/?unread_only=true",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        # é©—è??€?‰è??ç??šçŸ¥?½æ˜¯?ªè???
        for notif in result["notifications"]:
            assert notif["is_read"] is False
    
    @pytest.mark.asyncio
    async def test_get_notifications_unauthenticated(self, async_client: AsyncClient):
        """æ¸¬è©¦?ªè?è­‰ç”¨?¶ç²?–é€šçŸ¥"""
        response = await async_client.get("/api/v2/notifications/")
        
        # ?¹æ?å¯¦ä?ï¼Œå¯?½è???401 ?–ç©º?—è¡¨
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            result = response.json()
            assert result["notifications"] == []
            assert result["total"] == 0


class TestUnreadCountAPI:
    """?ªè?è¨ˆæ•¸ API æ¸¬è©¦"""
    
    @pytest.mark.asyncio
    async def test_get_unread_count_success(
        self, async_client: AsyncClient, adopter_auth_headers: dict
    ):
        """æ¸¬è©¦?²å??ªè?è¨ˆæ•¸"""
        response = await async_client.get(
            "/api/v2/notifications/unread-count",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "unread_count" in result
        assert isinstance(result["unread_count"], int)
        assert result["unread_count"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_unread_count_unauthenticated(self, async_client: AsyncClient):
        """æ¸¬è©¦?ªè?è­‰ç”¨?¶ç²?–æœªè®€è¨ˆæ•¸"""
        response = await async_client.get("/api/v2/notifications/unread-count")
        
        assert response.status_code in [200, 401]


class TestMarkAsReadAPI:
    """æ¨™è?å·²è? API æ¸¬è©¦"""
    
    @pytest.mark.asyncio
    async def test_mark_single_notification_as_read(
        self, async_client: AsyncClient, adopter_auth_headers: dict, db_session
    ):
        """æ¸¬è©¦æ¨™è??®å€‹é€šçŸ¥?ºå·²è®€"""
        # ?ˆç²?–ä??‹æœªè®€?šçŸ¥
        list_response = await async_client.get(
            "/api/v2/notifications/?unread_only=true",
            headers=adopter_auth_headers
        )
        
        if list_response.status_code == 200:
            notifications = list_response.json()["notifications"]
            if len(notifications) > 0:
                notification_id = notifications[0]["id"]
                
                # æ¨™è??ºå·²è®€
                response = await async_client.put(
                    f"/api/v2/notifications/{notification_id}/read",
                    headers=adopter_auth_headers
                )
                
                assert response.status_code in [200, 204]
                
                # é©—è?å·²æ?è¨?
                check_response = await async_client.get(
                    "/api/v2/notifications/",
                    headers=adopter_auth_headers
                )
                assert check_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_mark_nonexistent_notification_as_read(
        self, async_client: AsyncClient, adopter_auth_headers: dict
    ):
        """æ¸¬è©¦æ¨™è?ä¸å??¨ç??šçŸ¥?ºå·²è®€"""
        response = await async_client.put(
            "/api/v2/notifications/999999/read",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_mark_other_user_notification_as_read(
        self, async_client: AsyncClient, adopter_auth_headers: dict, shelter_auth_headers: dict, db_session
    ):
        """æ¸¬è©¦æ¨™è??¶ä??¨æˆ¶?„é€šçŸ¥?ºå·²è®€ï¼ˆæ??æ¸¬è©¦ï?"""
        # ?²å? adopter ?„é€šçŸ¥
        list_response = await async_client.get(
            "/api/v2/notifications/",
            headers=adopter_auth_headers
        )
        
        if list_response.status_code == 200:
            notifications = list_response.json()["notifications"]
            if len(notifications) > 0:
                notification_id = notifications[0]["id"]
                
                # shelter ?¨æˆ¶?—è©¦æ¨™è? adopter ?„é€šçŸ¥
                response = await async_client.put(
                    f"/api/v2/notifications/{notification_id}/read",
                    headers=shelter_auth_headers
                )
                
                # ?‰è©²è¢«æ?çµ?
                assert response.status_code in [403, 404]
    
    @pytest.mark.asyncio
    async def test_mark_all_notifications_as_read(
        self, async_client: AsyncClient, adopter_auth_headers: dict
    ):
        """æ¸¬è©¦æ¨™è??€?‰é€šçŸ¥?ºå·²è®€"""
        response = await async_client.post(
            "/api/v2/notifications/mark-all-read",
            headers=adopter_auth_headers
        )
        
        assert response.status_code in [200, 204]
        
        # é©—è??ªè?è¨ˆæ•¸??0
        count_response = await async_client.get(
            "/api/v2/notifications/unread-count",
            headers=adopter_auth_headers
        )
        
        if count_response.status_code == 200:
            result = count_response.json()
            assert result["unread_count"] == 0


class TestDeleteNotificationAPI:
    """?ªé™¤?šçŸ¥ API æ¸¬è©¦"""
    
    @pytest.mark.asyncio
    async def test_delete_notification_success(
        self, async_client: AsyncClient, adopter_auth_headers: dict, db_session
    ):
        """æ¸¬è©¦?å??ªé™¤?šçŸ¥"""
        # ?ˆç²?–é€šçŸ¥?—è¡¨
        list_response = await async_client.get(
            "/api/v2/notifications/",
            headers=adopter_auth_headers
        )
        
        if list_response.status_code == 200:
            notifications = list_response.json()["notifications"]
            if len(notifications) > 0:
                notification_id = notifications[0]["id"]
                initial_total = list_response.json()["total"]
                
                # ?ªé™¤?šçŸ¥
                response = await async_client.delete(
                    f"/api/v2/notifications/{notification_id}",
                    headers=adopter_auth_headers
                )
                
                assert response.status_code in [200, 204]
                
                # é©—è?å·²åˆª??
                check_response = await async_client.get(
                    "/api/v2/notifications/",
                    headers=adopter_auth_headers
                )
                
                if check_response.status_code == 200:
                    new_total = check_response.json()["total"]
                    assert new_total == initial_total - 1
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_notification(
        self, async_client: AsyncClient, adopter_auth_headers: dict
    ):
        """æ¸¬è©¦?ªé™¤ä¸å??¨ç??šçŸ¥"""
        response = await async_client.delete(
            "/api/v2/notifications/999999",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_other_user_notification(
        self, async_client: AsyncClient, adopter_auth_headers: dict, shelter_auth_headers: dict, db_session
    ):
        """æ¸¬è©¦?ªé™¤?¶ä??¨æˆ¶?„é€šçŸ¥ï¼ˆæ??æ¸¬è©¦ï?"""
        # ?²å? adopter ?„é€šçŸ¥
        list_response = await async_client.get(
            "/api/v2/notifications/",
            headers=adopter_auth_headers
        )
        
        if list_response.status_code == 200:
            notifications = list_response.json()["notifications"]
            if len(notifications) > 0:
                notification_id = notifications[0]["id"]
                
                # shelter ?¨æˆ¶?—è©¦?ªé™¤ adopter ?„é€šçŸ¥
                response = await async_client.delete(
                    f"/api/v2/notifications/{notification_id}",
                    headers=shelter_auth_headers
                )
                
                # ?‰è©²è¢«æ?çµ?
                assert response.status_code in [403, 404]


class TestNotificationIntegration:
    """?šçŸ¥ç³»çµ±?´å?æ¸¬è©¦"""
    
    @pytest.mark.asyncio
    async def test_notification_created_on_application_submission(
        self, async_client: AsyncClient, adopter_auth_headers: dict, shelter_auth_headers: dict, db_session
    ):
        """æ¸¬è©¦?äº¤?˜é??³è??‚å‰µå»ºé€šçŸ¥"""
        # shelter ?µå»ºå¯µç‰©
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
            headers=shelter_auth_headers
        )
        
        if pet_response.status_code == 201:
            pet_id = pet_response.json()["id"]
            
            # adopter ?äº¤?˜é??³è?
            application_data = {
                "pet_id": pet_id,
                "message": "I want to adopt this pet"
            }
            app_response = await async_client.post(
                "/api/v2/adoptions/applications",
                json=application_data,
                headers=adopter_auth_headers
            )
            
            assert app_response.status_code == 201
            
            # æª¢æŸ¥ shelter ?¯å¦?¶åˆ°?šçŸ¥
            notif_response = await async_client.get(
                "/api/v2/notifications/",
                headers=shelter_auth_headers
            )
            
            if notif_response.status_code == 200:
                notifications = notif_response.json()["notifications"]
                # ?‰è©²?‰æ–°?³è??„é€šçŸ¥
                assert any("application" in str(n).lower() for n in notifications)
    
    @pytest.mark.asyncio
    async def test_notification_pagination_boundary(
        self, async_client: AsyncClient, adopter_auth_headers: dict
    ):
        """æ¸¬è©¦?†é??Šç?æ¢ä»¶"""
        # æ¸¬è©¦ limit=0
        response = await async_client.get(
            "/api/v2/notifications/?limit=0",
            headers=adopter_auth_headers
        )
        assert response.status_code in [200, 400]
        
        # æ¸¬è©¦ skip è¶…é?ç¸½æ•¸
        response = await async_client.get(
            "/api/v2/notifications/?skip=999999",
            headers=adopter_auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert result["notifications"] == []
    
    @pytest.mark.asyncio
    async def test_notification_fields_completeness(
        self, async_client: AsyncClient, adopter_auth_headers: dict
    ):
        """æ¸¬è©¦?šçŸ¥?…å«?€?‰å?è¦æ?ä½?""
        response = await async_client.get(
            "/api/v2/notifications/",
            headers=adopter_auth_headers
        )
        
        if response.status_code == 200:
            notifications = response.json()["notifications"]
            if len(notifications) > 0:
                notif = notifications[0]
                # é©—è?å¿…è?æ¬„ä?
                assert "id" in notif
                assert "user_id" in notif
                assert "notification_type" in notif
                assert "title" in notif
                assert "message" in notif
                assert "is_read" in notif
                assert "created_at" in notif
