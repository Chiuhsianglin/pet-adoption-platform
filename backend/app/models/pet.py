"""
Pet model for managing pet information and adoption status
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, DECIMAL, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, declared_attr
import enum
from decimal import Decimal
from datetime import datetime

from app.database import Base


class PetSpecies(str, enum.Enum):
    """Pet species enumeration"""
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    RABBIT = "rabbit"
    HAMSTER = "hamster"
    FISH = "fish"
    REPTILE = "reptile"
    OTHER = "other"


class PetGender(str, enum.Enum):
    """Pet gender enumeration"""
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class PetSize(str, enum.Enum):
    """Pet size enumeration"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"


class EnergyLevel(str, enum.Enum):
    """Energy level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PetStatus(str, enum.Enum):
    """Pet adoption status enumeration"""
    DRAFT = "draft"  # 草稿
    PENDING_REVIEW = "pending_review"  # 待審核
    AVAILABLE = "available"  # 可領養
    PENDING = "pending"  # 領養申請中
    ADOPTED = "adopted"  # 已領養
    UNAVAILABLE = "unavailable"  # 暫停
    REJECTED = "rejected"  # 審核未通過


class Pet(Base):
    """Pet model for managing pet information"""
    
    __tablename__ = "pets"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(100), nullable=False, index=True)
    species = Column(Enum(PetSpecies, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    breed = Column(String(100), index=True)
    age_years = Column(Integer)  # 出生年份 (Birth Year) - e.g., 2023
    age_months = Column(Integer)  # 出生月份 (Birth Month) - e.g., 8 for August
    gender = Column(Enum(PetGender, values_callable=lambda x: [e.value for e in x]), index=True)
    size = Column(Enum(PetSize, values_callable=lambda x: [e.value for e in x]), index=True)
    weight_kg = Column(Float)  # Database type: float (NOT DECIMAL)
    color = Column(String(100))
    
    # Description and characteristics
    description = Column(Text)
    medical_info = Column(Text)  # Database column name (NOT health_status)
    behavioral_info = Column(Text)
    vaccination_status = Column(String(100))  # Database type: varchar(100) (NOT Boolean)
    spayed_neutered = Column(Boolean, default=False)  # Database column name (NOT sterilized)
    special_needs = Column(Text)
    
    # Additional pet characteristics from database
    microchip_id = Column(String(50))
    house_trained = Column(Boolean)
    good_with_kids = Column(Boolean)
    good_with_pets = Column(Boolean)
    energy_level = Column(Enum(EnergyLevel, values_callable=lambda x: [e.value for e in x]))  # Use enum instead of String
    
    # Adoption information
    adoption_fee = Column(DECIMAL(10, 2))
    status = Column(Enum(PetStatus, values_callable=lambda x: [e.value for e in x]), default=PetStatus.DRAFT, nullable=False, index=True)
    
    # Ownership
    shelter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Version control for optimistic locking
    version = Column(Integer, default=1, nullable=False)
    last_modified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships (no name conflicts now)
    shelter = relationship("User", back_populates="pets", foreign_keys=[shelter_id])
    creator = relationship("User", back_populates="created_pets", foreign_keys=[created_by])
    last_modifier = relationship("User", foreign_keys=[last_modified_by])
    photos = relationship("PetPhoto", back_populates="pet", cascade="all, delete-orphan")  # Photo objects
    adoption_applications = relationship("AdoptionApplication", back_populates="pet")
    favorites = relationship("UserFavorite", back_populates="pet")
    # Note: Old chat_rooms relationship removed - using new chat system with backref
    # chat_rooms = relationship("ChatRoom", back_populates="pet")
    # Note: community_posts removed - no foreign key relationship exists
    #statistics = relationship("PetStatistics", back_populates="pet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Pet(id={self.id}, name='{self.name}', species='{self.species}', status='{self.status}')>"
    
    @property
    def primary_photo(self) -> "PetPhoto":
        """Get primary photo"""
        for photo in self.photos:
            if photo.is_primary:
                return photo
        return self.photos[0] if self.photos else None
    
    @property
    def is_available(self) -> bool:
        """Check if pet is available for adoption"""
        return self.status == PetStatus.AVAILABLE


class PetPhoto(Base):
    """Pet photo model for managing pet images"""
    
    __tablename__ = "pet_photos"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Photo information
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False, index=True)
    file_url = Column(String(500), nullable=False)
    file_key = Column(String(255), nullable=False)  # S3 key or file identifier
    is_primary = Column(Boolean, default=False)
    caption = Column(String(255))
    upload_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    pet = relationship("Pet", back_populates="photos")
    
    def __repr__(self):
        return f"<PetPhoto(id={self.id}, pet_id={self.pet_id}, is_primary={self.is_primary})>"