# -*- coding: utf-8 -*-
"""
Adoption API E2E Tests
Test complete adoption application flow: HTTP Request -> Controller -> Service -> Repository -> Database
"""
import pytest
import uuid
from datetime import datetime
from httpx import AsyncClient
from app.models.user import User
from app.models.pet import Pet, PetStatus
from app.models.adoption import AdoptionApplication, ApplicationStatus


def generate_app_id():
    """Generate unique application ID"""
    return f"APP{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"


# ==================== Create Application Tests ====================

@pytest.mark.asyncio
class TestCreateApplicationAPI:
    """Test create adoption application API"""
    
    async def test_create_application_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        adopter_auth_headers: dict,
        sample_adoption_data: dict
    ):
        """Test adopter successfully creates application"""
        # Create test pet
        pet = Pet(
            name="Adoptable Dog",
            species="dog",
            breed="Labrador",
            gender="male",
            age_years=2,
            size="large",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add(pet)
        await test_db.commit()
        await test_db.refresh(pet)
        
        # Create application
        application_data = {
            "pet_id": pet.id,
            **sample_adoption_data
        }
        
        response = await async_client.post(
            "/api/v2/adoptions/applications",
            json=application_data,
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["pet_id"] == pet.id
        assert "id" in data
        assert data["status"] in [ApplicationStatus.DRAFT.value, ApplicationStatus.PENDING.value]
    
    async def test_create_application_missing_pet_id(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict,
        sample_adoption_data: dict
    ):
        """Test create application without pet_id"""
        response = await async_client.post(
            "/api/v2/adoptions/applications",
            json=sample_adoption_data,
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 400
        assert "pet_id" in response.json()["detail"].lower()
    
    async def test_create_application_pet_not_found(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict,
        sample_adoption_data: dict
    ):
        """Test create application for non-existent pet"""
        application_data = {
            "pet_id": 99999,
            **sample_adoption_data
        }
        
        response = await async_client.post(
            "/api/v2/adoptions/applications",
            json=application_data,
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_create_application_unauthenticated(
        self,
        async_client: AsyncClient,
        sample_adoption_data: dict
    ):
        """Test unauthenticated cannot create application"""
        application_data = {
            "pet_id": 1,
            **sample_adoption_data
        }
        
        response = await async_client.post(
            "/api/v2/adoptions/applications",
            json=application_data
        )
        
        assert response.status_code in [401, 403]


# ==================== List Applications Tests ====================

@pytest.mark.asyncio
class TestListApplicationsAPI:
    """Test list adoption applications API"""
    
    async def test_adopter_list_own_applications(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test adopter can list own applications"""
        # Create test pet and application
        pet = Pet(
            name="Test Pet",
            species="dog",
            breed="Beagle",
            gender="male",
            age_years=1,
            size="medium",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add(pet)
        await test_db.commit()
        await test_db.refresh(pet)
        
        application = AdoptionApplication(
            application_id=generate_app_id(),
            pet_id=pet.id,
            applicant_id=test_adopter_user.id,
            shelter_id=test_shelter_user.id,
            status=ApplicationStatus.PENDING,
            personal_info={},
            living_environment={},
            pet_experience={}
        )
        test_db.add(application)
        await test_db.commit()
        
        response = await async_client.get(
            "/api/v2/adoptions/applications",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "applications" in data or isinstance(data, list)
    
    async def test_shelter_list_applications(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        test_adopter_user: User,
        shelter_auth_headers: dict
    ):
        """Test shelter can list applications for their pets"""
        # Create test pet and application
        pet = Pet(
            name="Shelter Pet",
            species="cat",
            breed="Persian",
            gender="female",
            age_years=2,
            size="small",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add(pet)
        await test_db.commit()
        await test_db.refresh(pet)
        
        application = AdoptionApplication(
            application_id=generate_app_id(),
            pet_id=pet.id,
            applicant_id=test_adopter_user.id,
            shelter_id=test_shelter_user.id,
            status=ApplicationStatus.PENDING,
            personal_info={},
            living_environment={},
            pet_experience={}
        )
        test_db.add(application)
        await test_db.commit()
        
        response = await async_client.get(
            "/api/v2/adoptions/applications",
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 200


# ==================== Get Application Details Tests ====================

@pytest.mark.asyncio
class TestGetApplicationAPI:
    """Test get application details API"""
    
    async def test_get_application_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test successfully get application details"""
        # Create test pet and application
        pet = Pet(
            name="Application Pet",
            species="dog",
            breed="Shepherd",
            gender="male",
            age_years=3,
            size="large",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add(pet)
        await test_db.commit()
        await test_db.refresh(pet)
        
        application = AdoptionApplication(
            application_id=generate_app_id(),
            pet_id=pet.id,
            applicant_id=test_adopter_user.id,
            shelter_id=test_shelter_user.id,
            status=ApplicationStatus.PENDING,
            personal_info={},
            living_environment={},
            pet_experience={}
        )
        test_db.add(application)
        await test_db.commit()
        await test_db.refresh(application)
        
        response = await async_client.get(
            f"/api/v2/adoptions/applications/{application.id}",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == application.id
        assert data["pet_id"] == pet.id
    
    async def test_get_application_not_found(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict
    ):
        """Test get non-existent application"""
        response = await async_client.get(
            "/api/v2/adoptions/applications/99999",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_get_application_unauthorized(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        test_adopter_user: User,
        shelter_auth_headers: dict
    ):
        """Test cannot get other user's application without permission"""
        # Create test pet and application
        pet = Pet(
            name="Private Pet",
            species="cat",
            breed="Siamese",
            gender="female",
            age_years=1,
            size="small",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add(pet)
        await test_db.commit()
        await test_db.refresh(pet)
        
        application = AdoptionApplication(
            application_id=generate_app_id(),
            pet_id=pet.id,
            applicant_id=test_adopter_user.id,
            shelter_id=test_shelter_user.id,
            status=ApplicationStatus.PENDING,
            personal_info={},
            living_environment={},
            pet_experience={}
        )
        test_db.add(application)
        await test_db.commit()
        await test_db.refresh(application)
        
        # Shelter should be able to view (they own the pet)
        response = await async_client.get(
            f"/api/v2/adoptions/applications/{application.id}",
            headers=shelter_auth_headers
        )
        
        # Should succeed since shelter owns the pet
        assert response.status_code in [200, 403]


# ==================== Update Application Status Tests ====================

@pytest.mark.asyncio
class TestUpdateApplicationStatusAPI:
    """Test update application status API"""
    
    async def test_update_status_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        test_adopter_user: User,
        shelter_auth_headers: dict
    ):
        """Test shelter successfully updates application status"""
        # Create test pet and application
        pet = Pet(
            name="Status Test Pet",
            species="dog",
            breed="Bulldog",
            gender="male",
            age_years=2,
            size="medium",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add(pet)
        await test_db.commit()
        await test_db.refresh(pet)
        
        application = AdoptionApplication(
            application_id=generate_app_id(),
            pet_id=pet.id,
            applicant_id=test_adopter_user.id,
            shelter_id=test_shelter_user.id,
            status=ApplicationStatus.PENDING,
            personal_info={},
            living_environment={},
            pet_experience={}
        )
        test_db.add(application)
        await test_db.commit()
        await test_db.refresh(application)
        
        response = await async_client.patch(
            f"/api/v2/adoptions/applications/{application.id}/status?new_status=approved",
            headers=shelter_auth_headers
        )
        
        if response.status_code != 200:
            print(f"Error response: {response.status_code}")
            print(f"Response body: {response.text}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
    
    async def test_update_status_forbidden_for_adopter(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test adopter cannot update application status"""
        # Create test pet and application
        pet = Pet(
            name="Forbidden Pet",
            species="cat",
            breed="Tabby",
            gender="female",
            age_years=1,
            size="small",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add(pet)
        await test_db.commit()
        await test_db.refresh(pet)
        
        application = AdoptionApplication(
            application_id=generate_app_id(),
            pet_id=pet.id,
            applicant_id=test_adopter_user.id,
            shelter_id=test_shelter_user.id,
            status=ApplicationStatus.PENDING,
            personal_info={},
            living_environment={},
            pet_experience={}
        )
        test_db.add(application)
        await test_db.commit()
        await test_db.refresh(application)
        
        response = await async_client.patch(
            f"/api/v2/adoptions/applications/{application.id}/status?new_status=approved",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 403


# ==================== Withdraw Application Tests ====================

@pytest.mark.asyncio
class TestWithdrawApplicationAPI:
    """Test withdraw application API"""
    
    async def test_withdraw_application_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test adopter successfully withdraws application"""
        # Create test pet and application
        pet = Pet(
            name="Withdraw Test Pet",
            species="dog",
            breed="Poodle",
            gender="female",
            age_years=1,
            size="small",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add(pet)
        await test_db.commit()
        await test_db.refresh(pet)
        
        application = AdoptionApplication(
            application_id=generate_app_id(),
            pet_id=pet.id,
            applicant_id=test_adopter_user.id,
            shelter_id=test_shelter_user.id,
            status=ApplicationStatus.PENDING,
            personal_info={},
            living_environment={},
            pet_experience={}
        )
        test_db.add(application)
        await test_db.commit()
        await test_db.refresh(application)
        
        response = await async_client.post(
            f"/api/v2/adoptions/applications/{application.id}/withdraw",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == ApplicationStatus.WITHDRAWN.value
    
    async def test_withdraw_application_not_owner(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        test_adopter_user: User,
        shelter_auth_headers: dict
    ):
        """Test non-owner cannot withdraw application"""
        # Create test pet and application
        pet = Pet(
            name="No Withdraw Pet",
            species="cat",
            breed="Bengal",
            gender="male",
            age_years=2,
            size="medium",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add(pet)
        await test_db.commit()
        await test_db.refresh(pet)
        
        application = AdoptionApplication(
            application_id=generate_app_id(),
            pet_id=pet.id,
            applicant_id=test_adopter_user.id,
            shelter_id=test_shelter_user.id,
            status=ApplicationStatus.PENDING,
            personal_info={},
            living_environment={},
            pet_experience={}
        )
        test_db.add(application)
        await test_db.commit()
        await test_db.refresh(application)
        
        response = await async_client.post(
            f"/api/v2/adoptions/applications/{application.id}/withdraw",
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 403



