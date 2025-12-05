"""
Complete Adoption Workflow E2E Tests
完整領養業務流程端對端測試
"""
import pytest
from httpx import AsyncClient


class TestCompleteAdoptionWorkflow:
    """完整領養流程測試"""
    
    @pytest.mark.asyncio
    async def test_full_adoption_workflow_approved(
        self, async_client: AsyncClient, db_session
    ):
        """
        測試完整的領養流程 - 批准場景
        流程: 註冊 → 瀏覽寵物 → 申請 → 聊天 → 審核批准 → 通知
        """
        # 1. Shelter 註冊
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
        shelter_headers = {"Authorization": f"Bearer {shelter_token}"}
        
        # 2. Adopter 註冊
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
        adopter_headers = {"Authorization": f"Bearer {adopter_token}"}
        
        # 3. Shelter 發布寵物
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
            headers=shelter_headers
        )
        assert pet_response.status_code == 201
        pet_id = pet_response.json()["id"]
        
        # 4. Adopter 瀏覽寵物列表
        pets_list = await async_client.get("/api/v2/pets")
        assert pets_list.status_code == 200
        assert len(pets_list.json()["pets"]) > 0
        
        # 5. Adopter 查看寵物詳情
        pet_detail = await async_client.get(
            f"/api/v2/pets/{pet_id}",
            headers=adopter_headers
        )
        assert pet_detail.status_code == 200
        assert pet_detail.json()["name"] == "Workflow Test Dog"
        
        # 6. Adopter 提交領養申請
        application_data = {
            "pet_id": pet_id,
            "message": "I would love to adopt this dog. I have a large backyard."
        }
        app_response = await async_client.post(
            "/api/v2/adoptions/applications",
            json=application_data,
            headers=adopter_headers
        )
        assert app_response.status_code == 201
        application_id = app_response.json()["id"]
        assert app_response.json()["status"] == "pending"
        
        # 7. Shelter 查看收到的申請
        shelter_apps = await async_client.get(
            "/api/v2/adoptions/applications",
            headers=shelter_headers
        )
        assert shelter_apps.status_code == 200
        assert len(shelter_apps.json()["applications"]) > 0
        
        # 8. 創建聊天室進行溝通
        chat_data = {"pet_id": pet_id}
        chat_response = await async_client.post(
            "/api/v2/chat/rooms",
            json=chat_data,
            headers=adopter_headers
        )
        assert chat_response.status_code in [200, 201]
        room_id = chat_response.json()["id"]
        
        # 9. Adopter 發送訊息
        message_data = {
            "room_id": room_id,
            "content": "Hello, I submitted an adoption application. Can we schedule a visit?"
        }
        msg_response = await async_client.post(
            "/api/v2/chat/messages",
            json=message_data,
            headers=adopter_headers
        )
        assert msg_response.status_code in [200, 201]
        
        # 10. Shelter 回覆訊息
        reply_data = {
            "room_id": room_id,
            "content": "Sure! How about this Saturday at 2 PM?"
        }
        reply_response = await async_client.post(
            "/api/v2/chat/messages",
            json=reply_data,
            headers=shelter_headers
        )
        assert reply_response.status_code in [200, 201]
        
        # 11. Shelter 批准申請
        update_data = {"status": "approved"}
        update_response = await async_client.put(
            f"/api/v2/adoptions/applications/{application_id}/status",
            json=update_data,
            headers=shelter_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "approved"
        
        # 12. 驗證寵物狀態更新為 adopted
        pet_status = await async_client.get(
            f"/api/v2/pets/{pet_id}",
            headers=shelter_headers
        )
        assert pet_status.status_code == 200
        # 寵物應該標記為已領養或待領養
        assert pet_status.json()["status"] in ["adopted", "pending"]
        
        # 13. Adopter 檢查通知
        notifications = await async_client.get(
            "/api/v2/notifications/",
            headers=adopter_headers
        )
        if notifications.status_code == 200:
            notif_list = notifications.json()["notifications"]
            # 應該收到申請批准的通知
            assert any("approved" in str(n).lower() or "批准" in str(n).lower() 
                      for n in notif_list)
    
    @pytest.mark.asyncio
    async def test_full_adoption_workflow_rejected(
        self, async_client: AsyncClient, db_session
    ):
        """
        測試完整的領養流程 - 拒絕場景
        流程: 註冊 → 申請 → 審核拒絕 → 通知
        """
        # 1. Shelter 註冊
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
        shelter_headers = {"Authorization": f"Bearer {shelter_token}"}
        
        # 2. Adopter 註冊
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
        adopter_headers = {"Authorization": f"Bearer {adopter_token}"}
        
        # 3. Shelter 發布寵物
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
            headers=shelter_headers
        )
        assert pet_response.status_code == 201
        pet_id = pet_response.json()["id"]
        
        # 4. Adopter 提交領養申請
        application_data = {
            "pet_id": pet_id,
            "message": "I want to adopt this cat."
        }
        app_response = await async_client.post(
            "/api/v2/adoptions/applications",
            json=application_data,
            headers=adopter_headers
        )
        assert app_response.status_code == 201
        application_id = app_response.json()["id"]
        
        # 5. Shelter 拒絕申請
        update_data = {
            "status": "rejected",
            "rejection_reason": "Applicant does not meet requirements"
        }
        update_response = await async_client.put(
            f"/api/v2/adoptions/applications/{application_id}/status",
            json=update_data,
            headers=shelter_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "rejected"
        
        # 6. 驗證寵物仍然可供領養
        pet_status = await async_client.get(
            f"/api/v2/pets/{pet_id}",
            headers=shelter_headers
        )
        assert pet_status.status_code == 200
        assert pet_status.json()["status"] == "available"
        
        # 7. Adopter 可以查看被拒絕的申請
        app_detail = await async_client.get(
            f"/api/v2/adoptions/applications/{application_id}",
            headers=adopter_headers
        )
        assert app_detail.status_code == 200
        assert app_detail.json()["status"] == "rejected"
    
    @pytest.mark.asyncio
    async def test_workflow_adopter_withdraws_application(
        self, async_client: AsyncClient, db_session
    ):
        """
        測試領養人撤回申請的流程
        """
        # 1. 快速設置（註冊用戶和寵物）
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
        shelter_headers = {"Authorization": f"Bearer {shelter_token}"}
        
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
        adopter_headers = {"Authorization": f"Bearer {adopter_token}"}
        
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
            headers=shelter_headers
        )
        pet_id = pet_response.json()["id"]
        
        # 2. Adopter 提交申請
        application_data = {
            "pet_id": pet_id,
            "message": "I want to adopt."
        }
        app_response = await async_client.post(
            "/api/v2/adoptions/applications",
            json=application_data,
            headers=adopter_headers
        )
        application_id = app_response.json()["id"]
        
        # 3. Adopter 撤回申請
        withdraw_response = await async_client.post(
            f"/api/v2/adoptions/applications/{application_id}/withdraw",
            headers=adopter_headers
        )
        assert withdraw_response.status_code in [200, 204]
        
        # 4. 驗證申請狀態變為 withdrawn
        app_detail = await async_client.get(
            f"/api/v2/adoptions/applications/{application_id}",
            headers=adopter_headers
        )
        assert app_detail.status_code == 200
        assert app_detail.json()["status"] == "withdrawn"
    
    @pytest.mark.asyncio
    async def test_workflow_multiple_applicants_one_pet(
        self, async_client: AsyncClient, db_session
    ):
        """
        測試多個用戶申請同一隻寵物的流程
        """
        # 1. Shelter 註冊並發布寵物
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
        shelter_headers = {"Authorization": f"Bearer {shelter_token}"}
        
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
            headers=shelter_headers
        )
        pet_id = pet_response.json()["id"]
        
        # 2. 第一個 Adopter 註冊並申請
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
        
        # 3. 第二個 Adopter 註冊並申請
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
        
        # 4. Shelter 查看所有申請
        all_apps = await async_client.get(
            "/api/v2/adoptions/applications",
            headers=shelter_headers
        )
        assert all_apps.status_code == 200
        assert len(all_apps.json()["applications"]) >= 2
        
        # 5. Shelter 批准第一個申請
        approve_response = await async_client.put(
            f"/api/v2/adoptions/applications/{app1_id}/status",
            json={"status": "approved"},
            headers=shelter_headers
        )
        assert approve_response.status_code == 200
        
        # 6. 第二個申請應該自動被拒絕或仍然可以手動處理
        app2_detail = await async_client.get(
            f"/api/v2/adoptions/applications/{app2_id}",
            headers=adopter2_headers
        )
        assert app2_detail.status_code == 200
        # 狀態應該是 pending 或 rejected
        assert app2_detail.json()["status"] in ["pending", "rejected"]
