"""
Pet model for managing pet information and adoption status
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from decimal import Decimal

from app.database import Base


class PetSpecies(str, enum.Enum):
    """Pet species enumeration"""
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    RABBIT = "rabbit"
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


class PetStatus(str, enum.Enum):
    """Pet adoption status enumeration"""
    AVAILABLE = "available"
    PENDING = "pending"
    ADOPTED = "adopted"
    UNAVAILABLE = "unavailable"


class Pet(Base):
    """Pet model for managing pet information"""
    
    __tablename__ = "pets"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(100), nullable=False, index=True)
    species = Column(Enum(PetSpecies), nullable=False, index=True)
    breed = Column(String(100), index=True)
    age_months = Column(Integer)
    gender = Column(Enum(PetGender), index=True)
    size = Column(Enum(PetSize), index=True)
    color = Column(String(100))
    
    # Description and characteristics
    description = Column(Text)
    health_status = Column(Text)
    vaccination_status = Column(Boolean, default=False)
    sterilized = Column(Boolean, default=False)
    special_needs = Column(Text)
    
    # Adoption information
    adoption_fee = Column(DECIMAL(10, 2))
    status = Column(Enum(PetStatus), default=PetStatus.AVAILABLE, nullable=False, index=True)
    
    # Location and ownership
    location = Column(String(255), index=True)
    shelter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    shelter = relationship("User", back_populates="pets", foreign_keys=[shelter_id])
    creator = relationship("User", back_populates="created_pets", foreign_keys=[created_by])
    photos = relationship("PetPhoto", back_populates="pet", cascade="all, delete-orphan")
    adoption_applications = relationship("AdoptionApplication", back_populates="pet")
    favorites = relationship("UserFavorite", back_populates="pet")
    chat_rooms = relationship("ChatRoom", back_populates="pet")
    
    def __repr__(self):
        return f"<Pet(id={self.id}, name='{self.name}', species='{self.species}', status='{self.status}')>"
    
    @property
    def age_years(self) -> float:
        """Calculate age in years"""
        if self.age_months:
            return round(self.age_months / 12, 1)
        return 0.0
    
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