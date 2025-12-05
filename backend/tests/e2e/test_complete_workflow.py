"""
Complete Adoption Workflow E2E Tests
å®Œæ•´?˜é?æ¥­å?æµç?ç«¯å?ç«¯æ¸¬è©?
"""
import pytest
from httpx import AsyncClient


class TestCompleteAdoptionWorkflow:
    """å®Œæ•´?˜é?æµç?æ¸¬è©¦"""
    
    @pytest.mark.asyncio
    async def test_full_adoption_workflow_approved(
        self, async_client: AsyncClient, db_session
    ):
        """
        æ¸¬è©¦å®Œæ•´?„é?é¤Šæ?ç¨?- ?¹å??´æ™¯
        æµç?: è¨»å? ???è¦½å¯µç‰© ???³è? ???Šå¤© ??å¯©æ ¸?¹å? ???šçŸ¥
        """
        # 1. Shelter è¨»å?
        shelter_register = {
            "email": "shelter_workflow@test.com",
            "password": "SecurePass123!",
            "name": "Test Shelter",
            "user_type": "shelter"
        }
        shelter_response = await async_client.post(
            "/api/v2/auth/register",
            json=shelter_register
        )
        assert shelter_response.status_code == 201
        shelter_token = shelter_response.json()["access_token"]
        shelter_auth_headers = {"Authorization": f"Bearer {shelter_token}"}
        
        # 2. Adopter è¨»å?
        adopter_register = {
            "email": "adopter_workflow@test.com",
            "password": "SecurePass123!",
            "name": "Test Adopter",
            "user_type": "adopter"
        }
        adopter_response = await async_client.post(
            "/api/v2/auth/register",
            json=adopter_register
        )
        assert adopter_response.status_code == 201
        adopter_token = adopter_response.json()["access_token"]
        adopter_auth_headers = {"Authorization": f"Bearer {adopter_token}"}
        
        # 3. Shelter ?¼å?å¯µç‰©
        pet_data = {
            "name": "Workflow Test Dog",
            "species": "dog",
            "breed": "Golden Retriever",
            "age": 3,
            "gender": "male",
            "description": "A friendly dog for adoption",
            "status": "available"
        }
        pet_response = await async_client.post(
            "/api/v2/pets",
            json=pet_data,
            headers=shelter_auth_headers
        )
        assert pet_response.status_code == 201
        pet_id = pet_response.json()["id"]
        
        # 4. Adopter ?è¦½å¯µç‰©?—è¡¨
        pets_list = await async_client.get("/api/v2/pets")
        assert pets_list.status_code == 200
        assert len(pets_list.json()["pets"]) > 0
        
        # 5. Adopter ?¥ç?å¯µç‰©è©³æ?
        pet_detail = await async_client.get(
            f"/api/v2/pets/{pet_id}",
            headers=adopter_auth_headers
        )
        assert pet_detail.status_code == 200
        assert pet_detail.json()["name"] == "Workflow Test Dog"
        
        # 6. Adopter ?äº¤?˜é??³è?
        application_data = {
            "pet_id": pet_id,
            "message": "I would love to adopt this dog. I have a large backyard."
        }
        app_response = await async_client.post(
            "/api/v2/adoptions/applications",
            json=application_data,
            headers=adopter_auth_headers
        )
        assert app_response.status_code == 201
        application_id = app_response.json()["id"]
        assert app_response.json()["status"] == "pending"
        
        # 7. Shelter ?¥ç??¶åˆ°?„ç”³è«?
        shelter_apps = await async_client.get(
            "/api/v2/adoptions/applications",
            headers=shelter_auth_headers
        )
        assert shelter_apps.status_code == 200
        assert len(shelter_apps.json()["applications"]) > 0
        
        # 8. ?µå»º?Šå¤©å®¤é€²è?æºé€?
        chat_data = {"pet_id": pet_id}
        chat_response = await async_client.post(
            "/api/v2/chat/rooms",
            json=chat_data,
            headers=adopter_auth_headers
        )
        assert chat_response.status_code in [200, 201]
        room_id = chat_response.json()["id"]
        
        # 9. Adopter ?¼é€è???
        message_data = {
            "room_id": room_id,
            "content": "Hello, I submitted an adoption application. Can we schedule a visit?"
        }
        msg_response = await async_client.post(
            "/api/v2/chat/messages",
            json=message_data,
            headers=adopter_auth_headers
        )
        assert msg_response.status_code in [200, 201]
        
        # 10. Shelter ?è?è¨Šæ¯
        reply_data = {
            "room_id": room_id,
            "content": "Sure! How about this Saturday at 2 PM?"
        }
        reply_response = await async_client.post(
            "/api/v2/chat/messages",
            json=reply_data,
            headers=shelter_auth_headers
        )
        assert reply_response.status_code in [200, 201]
        
        # 11. Shelter ?¹å??³è?
        update_data = {"status": "approved"}
        update_response = await async_client.put(
            f"/api/v2/adoptions/applications/{application_id}/status",
            json=update_data,
            headers=shelter_auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "approved"
        
        # 12. é©—è?å¯µç‰©?€?‹æ›´?°ç‚º adopted
        pet_status = await async_client.get(
            f"/api/v2/pets/{pet_id}",
            headers=shelter_auth_headers
        )
        assert pet_status.status_code == 200
        # å¯µç‰©?‰è©²æ¨™è??ºå·²?˜é??–å??˜é?
        assert pet_status.json()["status"] in ["adopted", "pending"]
        
        # 13. Adopter æª¢æŸ¥?šçŸ¥
        notifications = await async_client.get(
            "/api/v2/notifications/",
            headers=adopter_auth_headers
        )
        if notifications.status_code == 200:
            notif_list = notifications.json()["notifications"]
            # ?‰è©²?¶åˆ°?³è??¹å??„é€šçŸ¥
            assert any("approved" in str(n).lower() or "?¹å?" in str(n).lower() 
                      for n in notif_list)
    
    @pytest.mark.asyncio
    async def test_full_adoption_workflow_rejected(
        self, async_client: AsyncClient, db_session
    ):
        """
        æ¸¬è©¦å®Œæ•´?„é?é¤Šæ?ç¨?- ?’ç??´æ™¯
        æµç?: è¨»å? ???³è? ??å¯©æ ¸?’ç? ???šçŸ¥
        """
        # 1. Shelter è¨»å?
        shelter_register = {
            "email": "shelter_reject@test.com",
            "password": "SecurePass123!",
            "name": "Reject Test Shelter",
            "user_type": "shelter"
        }
        shelter_response = await async_client.post(
            "/api/v2/auth/register",
            json=shelter_register
        )
        assert shelter_response.status_code == 201
        shelter_token = shelter_response.json()["access_token"]
        shelter_auth_headers = {"Authorization": f"Bearer {shelter_token}"}
        
        # 2. Adopter è¨»å?
        adopter_register = {
            "email": "adopter_reject@test.com",
            "password": "SecurePass123!",
            "name": "Reject Test Adopter",
            "user_type": "adopter"
        }
        adopter_response = await async_client.post(
            "/api/v2/auth/register",
            json=adopter_register
        )
        assert adopter_response.status_code == 201
        adopter_token = adopter_response.json()["access_token"]
        adopter_auth_headers = {"Authorization": f"Bearer {adopter_token}"}
        
        # 3. Shelter ?¼å?å¯µç‰©
        pet_data = {
            "name": "Reject Test Cat",
            "species": "cat",
            "breed": "Persian",
            "age": 2,
            "gender": "female",
            "description": "Beautiful Persian cat"
        }
        pet_response = await async_client.post(
            "/api/v2/pets",
            json=pet_data,
            headers=shelter_auth_headers
        )
        assert pet_response.status_code == 201
        pet_id = pet_response.json()["id"]
        
        # 4. Adopter ?äº¤?˜é??³è?
        application_data = {
            "pet_id": pet_id,
            "message": "I want to adopt this cat."
        }
        app_response = await async_client.post(
            "/api/v2/adoptions/applications",
            json=application_data,
            headers=adopter_auth_headers
        )
        assert app_response.status_code == 201
        application_id = app_response.json()["id"]
        
        # 5. Shelter ?’ç??³è?
        update_data = {
            "status": "rejected",
            "rejection_reason": "Applicant does not meet requirements"
        }
        update_response = await async_client.put(
            f"/api/v2/adoptions/applications/{application_id}/status",
            json=update_data,
            headers=shelter_auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "rejected"
        
        # 6. é©—è?å¯µç‰©ä»ç„¶?¯ä??˜é?
        pet_status = await async_client.get(
            f"/api/v2/pets/{pet_id}",
            headers=shelter_auth_headers
        )
        assert pet_status.status_code == 200
        assert pet_status.json()["status"] == "available"
        
        # 7. Adopter ?¯ä»¥?¥ç?è¢«æ?çµ•ç??³è?
        app_detail = await async_client.get(
            f"/api/v2/adoptions/applications/{application_id}",
            headers=adopter_auth_headers
        )
        assert app_detail.status_code == 200
        assert app_detail.json()["status"] == "rejected"
    
    @pytest.mark.asyncio
    async def test_workflow_adopter_withdraws_application(
        self, async_client: AsyncClient, db_session
    ):
        """
        æ¸¬è©¦?˜é?äººæ’¤?ç”³è«‹ç?æµç?
        """
        # 1. å¿«é€Ÿè¨­ç½®ï?è¨»å??¨æˆ¶?Œå¯µ?©ï?
        shelter_register = {
            "email": "shelter_withdraw@test.com",
            "password": "SecurePass123!",
            "name": "Withdraw Test Shelter",
            "user_type": "shelter"
        }
        shelter_response = await async_client.post(
            "/api/v2/auth/register",
            json=shelter_register
        )
        shelter_token = shelter_response.json()["access_token"]
        shelter_auth_headers = {"Authorization": f"Bearer {shelter_token}"}
        
        adopter_register = {
            "email": "adopter_withdraw@test.com",
            "password": "SecurePass123!",
            "name": "Withdraw Test Adopter",
            "user_type": "adopter"
        }
        adopter_response = await async_client.post(
            "/api/v2/auth/register",
            json=adopter_register
        )
        adopter_token = adopter_response.json()["access_token"]
        adopter_auth_headers = {"Authorization": f"Bearer {adopter_token}"}
        
        pet_data = {
            "name": "Withdraw Test Pet",
            "species": "dog",
            "breed": "Beagle",
            "age": 1,
            "gender": "male",
            "description": "Test pet"
        }
        pet_response = await async_client.post(
            "/api/v2/pets",
            json=pet_data,
            headers=shelter_auth_headers
        )
        pet_id = pet_response.json()["id"]
        
        # 2. Adopter ?äº¤?³è?
        application_data = {
            "pet_id": pet_id,
            "message": "I want to adopt."
        }
        app_response = await async_client.post(
            "/api/v2/adoptions/applications",
            json=application_data,
            headers=adopter_auth_headers
        )
        application_id = app_response.json()["id"]
        
        # 3. Adopter ?¤å??³è?
        withdraw_response = await async_client.post(
            f"/api/v2/adoptions/applications/{application_id}/withdraw",
            headers=adopter_auth_headers
        )
        assert withdraw_response.status_code in [200, 204]
        
        # 4. é©—è??³è??€?‹è???withdrawn
        app_detail = await async_client.get(
            f"/api/v2/adoptions/applications/{application_id}",
            headers=adopter_auth_headers
        )
        assert app_detail.status_code == 200
        assert app_detail.json()["status"] == "withdrawn"
    
    @pytest.mark.asyncio
    async def test_workflow_multiple_applicants_one_pet(
        self, async_client: AsyncClient, db_session
    ):
        """
        æ¸¬è©¦å¤šå€‹ç”¨?¶ç”³è«‹å?ä¸€?»å¯µ?©ç?æµç?
        """
        # 1. Shelter è¨»å?ä¸¦ç™¼å¸ƒå¯µ??
        shelter_register = {
            "email": "shelter_multi@test.com",
            "password": "SecurePass123!",
            "name": "Multi Test Shelter",
            "user_type": "shelter"
        }
        shelter_response = await async_client.post(
            "/api/v2/auth/register",
            json=shelter_register
        )
        shelter_token = shelter_response.json()["access_token"]
        shelter_auth_headers = {"Authorization": f"Bearer {shelter_token}"}
        
        pet_data = {
            "name": "Popular Pet",
            "species": "dog",
            "breed": "Poodle",
            "age": 2,
            "gender": "female",
            "description": "Very popular pet"
        }
        pet_response = await async_client.post(
            "/api/v2/pets",
            json=pet_data,
            headers=shelter_auth_headers
        )
        pet_id = pet_response.json()["id"]
        
        # 2. ç¬¬ä???Adopter è¨»å?ä¸¦ç”³è«?
        adopter1_register = {
            "email": "adopter1_multi@test.com",
            "password": "SecurePass123!",
            "name": "Adopter One",
            "user_type": "adopter"
        }
        adopter1_response = await async_client.post(
            "/api/v2/auth/register",
            json=adopter1_register
        )
        adopter1_token = adopter1_response.json()["access_token"]
        adopter1_headers = {"Authorization": f"Bearer {adopter1_token}"}
        
        app1_response = await async_client.post(
            "/api/v2/adoptions/applications",
            json={"pet_id": pet_id, "message": "First applicant"},
            headers=adopter1_headers
        )
        assert app1_response.status_code == 201
        app1_id = app1_response.json()["id"]
        
        # 3. ç¬¬ä???Adopter è¨»å?ä¸¦ç”³è«?
        adopter2_register = {
            "email": "adopter2_multi@test.com",
            "password": "SecurePass123!",
            "name": "Adopter Two",
            "user_type": "adopter"
        }
        adopter2_response = await async_client.post(
            "/api/v2/auth/register",
            json=adopter2_register
        )
        adopter2_token = adopter2_response.json()["access_token"]
        adopter2_headers = {"Authorization": f"Bearer {adopter2_token}"}
        
        app2_response = await async_client.post(
            "/api/v2/adoptions/applications",
            json={"pet_id": pet_id, "message": "Second applicant"},
            headers=adopter2_headers
        )
        assert app2_response.status_code == 201
        app2_id = app2_response.json()["id"]
        
        # 4. Shelter ?¥ç??€?‰ç”³è«?
        all_apps = await async_client.get(
            "/api/v2/adoptions/applications",
            headers=shelter_auth_headers
        )
        assert all_apps.status_code == 200
        assert len(all_apps.json()["applications"]) >= 2
        
        # 5. Shelter ?¹å?ç¬¬ä??‹ç”³è«?
        approve_response = await async_client.put(
            f"/api/v2/adoptions/applications/{app1_id}/status",
            json={"status": "approved"},
            headers=shelter_auth_headers
        )
        assert approve_response.status_code == 200
        
        # 6. ç¬¬ä??‹ç”³è«‹æ?è©²è‡ª?•è¢«?’ç??–ä??¶å¯ä»¥æ??•è???
        app2_detail = await async_client.get(
            f"/api/v2/adoptions/applications/{app2_id}",
            headers=adopter2_headers
        )
        assert app2_detail.status_code == 200
        # ?€?‹æ?è©²æ˜¯ pending ??rejected
        assert app2_detail.json()["status"] in ["pending", "rejected"]
