# -*- coding: utf-8 -*-
"""
Pet API E2E Tests
Test complete pet management flow: HTTP Request -> Controller -> Service -> Repository -> Database
"""
import pytest
from httpx import AsyncClient
from app.models.user import User
from app.models.pet import Pet, PetStatus


# ==================== Create Pet Tests ====================

@pytest.mark.asyncio
class TestCreatePetAPI:
    """Test create pet API"""
    
    async def test_create_pet_success_by_shelter(
        self,
        async_client: AsyncClient,
        shelter_auth_headers: dict,
        sample_pet_data: dict
    ):
        """Test shelter successfully creates pet"""
        response = await async_client.post(
            "/api/v2/pets/",
            json=sample_pet_data,
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_pet_data["name"]
        assert data["species"] == sample_pet_data["species"]
        assert data["breed"] == sample_pet_data["breed"]
        assert data["gender"] == sample_pet_data["gender"]
        assert "id" in data
    
    async def test_create_pet_forbidden_for_adopter(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict,
        sample_pet_data: dict
    ):
        """Test adopter cannot create pet"""
        response = await async_client.post(
            "/api/v2/pets/",
            json=sample_pet_data,
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 403
    
    async def test_create_pet_unauthenticated(
        self,
        async_client: AsyncClient,
        sample_pet_data: dict
    ):
        """Test unauthenticated cannot create pet"""
        response = await async_client.post(
            "/api/v2/pets/",
            json=sample_pet_data
        )
        
        assert response.status_code in [401, 403]


# ==================== List Pets Tests ====================

@pytest.mark.asyncio
class TestListPetsAPI:
    """Test list pets API"""
    
    async def test_list_pets_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User
    ):
        """Test successfully list pets"""
        # Create test pets
        pet1 = Pet(
            name="Dog 1",
            species="dog",
            breed="Golden Retriever",
            gender="male",
            age_years=2,
            size="large",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        pet2 = Pet(
            name="Cat 1",
            species="cat",
            breed="Persian",
            gender="female",
            age_years=1,
            size="small",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add_all([pet1, pet2])
        await test_db.commit()
        
        response = await async_client.get("/api/v2/pets/")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert len(data["items"]) >= 2
    
    async def test_list_pets_with_filters(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User
    ):
        """Test list pets with filters"""
        # Create pets of different species
        dog = Pet(
            name="Test Dog",
            species="dog",
            breed="Labrador",
            gender="male",
            age_years=3,
            size="large",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        cat = Pet(
            name="Test Cat",
            species="cat",
            breed="Siamese",
            gender="female",
            age_years=2,
            size="medium",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add_all([dog, cat])
        await test_db.commit()
        
        # Filter dogs
        response = await async_client.get("/api/v2/pets/?species=dog")
        
        assert response.status_code == 200
        data = response.json()
        if data["total"] > 0:
            assert all(pet["species"] == "dog" for pet in data["items"])
    
    async def test_list_pets_pagination(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User
    ):
        """Test pagination"""
        # Create multiple pets
        pets = [
            Pet(
                name=f"Pet {i}",
                species="dog",
                breed="Mixed",
                gender="male" if i % 2 == 0 else "female",
                age_years=i,
                size="medium",
                status=PetStatus.AVAILABLE,
                shelter_id=test_shelter_user.id,
                created_by=test_shelter_user.id
            )
            for i in range(5)
        ]
        test_db.add_all(pets)
        await test_db.commit()
        
        # Test first page, 2 items per page
        response = await async_client.get("/api/v2/pets/?page=1&page_size=2")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) <= 2


# ==================== Get Pet Details Tests ====================

@pytest.mark.asyncio
class TestGetPetAPI:
    """Test get pet details API"""
    
    async def test_get_pet_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User
    ):
        """Test successfully get pet details"""
        # Create test pet
        pet = Pet(
            name="Lucky",
            species="dog",
            breed="Golden Retriever",
            gender="male",
            age_years=2,
            size="large",
            description="Friendly dog",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add(pet)
        await test_db.commit()
        await test_db.refresh(pet)
        
        response = await async_client.get(f"/api/v2/pets/{pet.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data  # V1 compatible format
        pet_data = data["data"]
        assert pet_data["name"] == "Lucky"
        assert pet_data["species"] == "dog"
        assert pet_data["id"] == pet.id
    
    async def test_get_pet_not_found(
        self,
        async_client: AsyncClient
    ):
        """Test pet not found"""
        response = await async_client.get("/api/v2/pets/99999")
        
        assert response.status_code == 404
    
    async def test_get_pet_with_authentication(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        adopter_auth_headers: dict
    ):
        """Test authenticated user get pet details (with favorite status)"""
        # Create test pet
        pet = Pet(
            name="Authenticated Pet",
            species="cat",
            breed="Persian",
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
        
        response = await async_client.get(
            f"/api/v2/pets/{pet.id}",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert "is_favorited" in data
        assert data["is_favorited"] is False


# ==================== Update Pet Tests ====================

@pytest.mark.asyncio
class TestUpdatePetAPI:
    """Test update pet API"""
    
    async def test_update_pet_success_by_owner(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        shelter_auth_headers: dict
    ):
        """Test owner successfully updates pet"""
        # Create test pet
        pet = Pet(
            name="Original Name",
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
        
        # Update pet
        update_data = {
            "name": "Updated Name",
            "age_years": 3,
            "description": "Updated description"
        }
        
        response = await async_client.put(
            f"/api/v2/pets/{pet.id}",
            json=update_data,
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["age_years"] == 3
    
    async def test_update_pet_forbidden_for_non_owner(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        adopter_auth_headers: dict
    ):
        """Test non-owner cannot update pet"""
        # Create test pet
        pet = Pet(
            name="Protected Pet",
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
        
        update_data = {"name": "Hacked Name"}
        
        response = await async_client.put(
            f"/api/v2/pets/{pet.id}",
            json=update_data,
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 403
    
    async def test_update_pet_not_found(
        self,
        async_client: AsyncClient,
        shelter_auth_headers: dict
    ):
        """Test update non-existent pet"""
        update_data = {"name": "Ghost Pet"}
        
        response = await async_client.put(
            "/api/v2/pets/99999",
            json=update_data,
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 404


# ==================== Delete Pet Tests ====================

@pytest.mark.asyncio
class TestDeletePetAPI:
    """Test delete pet API"""
    
    async def test_delete_pet_success_by_owner(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        shelter_auth_headers: dict
    ):
        """Test owner successfully deletes pet"""
        # Create test pet
        pet = Pet(
            name="To Be Deleted",
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
        pet_id = pet.id
        
        response = await async_client.delete(
            f"/api/v2/pets/{pet_id}",
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify pet is deleted
        get_response = await async_client.get(f"/api/v2/pets/{pet_id}")
        assert get_response.status_code == 404
    
    async def test_delete_pet_forbidden_for_non_owner(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User,
        adopter_auth_headers: dict
    ):
        """Test non-owner cannot delete pet"""
        # Create test pet
        pet = Pet(
            name="Protected Pet",
            species="cat",
            breed="Maine Coon",
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
        
        response = await async_client.delete(
            f"/api/v2/pets/{pet.id}",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 403
    
    async def test_delete_pet_not_found(
        self,
        async_client: AsyncClient,
        shelter_auth_headers: dict
    ):
        """Test delete non-existent pet"""
        response = await async_client.delete(
            "/api/v2/pets/99999",
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 404


# ==================== Permission Tests ====================

@pytest.mark.asyncio
class TestPetAPIPermissions:
    """Test pet API permission control"""
    
    async def test_unauthenticated_can_only_view(
        self,
        async_client: AsyncClient,
        test_db,
        test_shelter_user: User
    ):
        """Test unauthenticated user can only view pets"""
        # Create test pet
        pet = Pet(
            name="Public Pet",
            species="cat",
            breed="Tabby",
            gender="female",
            age_years=1,
            size="medium",
            status=PetStatus.AVAILABLE,
            shelter_id=test_shelter_user.id,
            created_by=test_shelter_user.id
        )
        test_db.add(pet)
        await test_db.commit()
        await test_db.refresh(pet)
        
        # Can view
        get_response = await async_client.get(f"/api/v2/pets/{pet.id}")
        assert get_response.status_code == 200
        
        # Cannot create
        create_response = await async_client.post(
            "/api/v2/pets/",
            json={"name": "New Pet", "species": "dog", "gender": "male"}
        )
        assert create_response.status_code in [401, 403]
        
        # Cannot update
        update_response = await async_client.put(
            f"/api/v2/pets/{pet.id}",
            json={"name": "Hacked"}
        )
        assert update_response.status_code in [401, 403]
