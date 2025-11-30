"""
Adoption application schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.adoption import ApplicationStatus


# Personal Info Schema
class PersonalInfoSchema(BaseModel):
    """Personal information section of adoption application"""
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: str = Field(..., min_length=5, max_length=100)
    address: str = Field(..., min_length=1, max_length=200)
    id_number: str = Field(..., min_length=1, max_length=20)
    occupation: str = Field(..., min_length=1, max_length=100)
    monthly_income: int = Field(..., ge=0)


# Living Environment Schema
class LivingEnvironmentSchema(BaseModel):
    """Living environment section of adoption application"""
    housing_type: str = Field(..., max_length=50)  # apartment, house, rental, owned
    space_size: int = Field(..., ge=0)  # square meters
    has_yard: bool
    family_members: int = Field(..., ge=1)
    has_allergies: bool
    other_pets: Optional[List[Dict[str, Any]]] = None
    environment_photos: Optional[List[Dict[str, Any]]] = None  # URLs and keys for environment photos


# Pet Experience Schema
class PetExperienceSchema(BaseModel):
    """Pet experience section of adoption application"""
    previous_experience: str = Field(..., min_length=1, max_length=1000)
    pet_knowledge: str = Field(..., min_length=1, max_length=1000)
    care_schedule: str = Field(..., min_length=1, max_length=1000)
    veterinarian_info: str = Field(..., min_length=1, max_length=500)
    emergency_fund: int = Field(..., ge=0)


# Adoption Application Create Schema
class AdoptionApplicationCreate(BaseModel):
    """Schema for creating a new adoption application"""
    pet_id: int = Field(..., gt=0)
    personal_info: PersonalInfoSchema
    living_environment: LivingEnvironmentSchema
    pet_experience: PetExperienceSchema


# Adoption Application Update Schema
class AdoptionApplicationUpdate(BaseModel):
    """Schema for updating an adoption application"""
    personal_info: Optional[PersonalInfoSchema] = None
    living_environment: Optional[LivingEnvironmentSchema] = None
    pet_experience: Optional[PetExperienceSchema] = None


# Adoption Application Response Schema
class AdoptionApplicationResponse(BaseModel):
    """Schema for adoption application response"""
    id: int
    application_id: str
    pet_id: int
    applicant_id: Optional[int] = None
    shelter_id: Optional[int] = None
    status: ApplicationStatus
    personal_info: Dict[str, Any]
    living_environment: Dict[str, Any]
    pet_experience: Dict[str, Any]
    review_notes: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    home_visit_date: Optional[datetime] = None
    home_visit_notes: Optional[str] = None
    home_visit_document: Optional[str] = None
    final_decision_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    pet: Optional[Dict[str, Any]] = Field(default=None)
    documents: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

    @field_validator('pet', mode='before')
    @classmethod
    def serialize_pet(cls, v):
        """Convert Pet model to dict"""
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        # Convert SQLAlchemy model to dict
        pet_dict = {
            'id': v.id,
            'name': v.name,
            'species': v.species.value if hasattr(v.species, 'value') else v.species,
            'breed': v.breed,
            'age_years': v.age_years,
            'age_months': v.age_months,
            'gender': v.gender.value if hasattr(v.gender, 'value') else v.gender,
            'size': v.size.value if hasattr(v.size, 'value') else v.size,
        }
        # Add photos if available
        if hasattr(v, 'photos') and v.photos:
            pet_dict['photos'] = [
                {
                    'id': photo.id,
                    'file_url': photo.file_url,
                    'is_primary': photo.is_primary
                } for photo in v.photos
            ]
        return pet_dict

    @field_validator('documents', mode='before')
    @classmethod
    def serialize_documents(cls, v):
        """Convert Document models to list of dicts"""
        if v is None:
            return []
        if isinstance(v, list) and all(isinstance(item, dict) for item in v):
            return v
        # Convert SQLAlchemy models to dicts
        return [
            {
                'id': doc.id,
                'application_id': doc.application_id,
                'document_type': doc.document_type,
                'file_name': doc.file_name,
                'file_url': doc.file_url,
                'file_key': doc.file_key,
                'uploaded_at': doc.uploaded_at.isoformat() if doc.uploaded_at else None,
            } for doc in v
        ]

    class Config:
        from_attributes = True


# Application List Response Schema
class AdoptionApplicationListResponse(BaseModel):
    """Schema for paginated adoption applications list"""
    applications: List[AdoptionApplicationResponse]
    total: int
    skip: int
    limit: int


# Application Document Schema
class ApplicationDocumentCreate(BaseModel):
    """Schema for creating application document"""
    document_type: str = Field(..., max_length=50)
    file_name: str = Field(..., max_length=255)
    file_url: str = Field(..., max_length=500)
    file_key: str = Field(..., max_length=255)
    file_size: Optional[int] = None
    mime_type: Optional[str] = Field(None, max_length=100)


class ApplicationDocumentResponse(BaseModel):
    """Schema for application document response"""
    id: int
    application_id: int
    document_type: str
    file_name: str
    original_filename: Optional[str] = None
    file_url: str
    file_key: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    uploaded_by: Optional[int] = None
    uploaded_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Default values for fields not in the database yet
    status: str = 'pending'
    version: int = 1
    is_current_version: bool = True
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True
