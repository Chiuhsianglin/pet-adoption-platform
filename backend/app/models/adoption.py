"""
Adoption application model for managing the adoption process
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from typing import Optional

from app.database import Base


class ApplicationStatus(str, enum.Enum):
    """Adoption application status enumeration"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class AdoptionApplication(Base):
    """Adoption application model"""
    
    __tablename__ = "adoption_applications"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Application identifier
    application_id = Column(String(20), unique=True, nullable=False, index=True)
    
    # Related entities
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False, index=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Application status
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.DRAFT, nullable=False, index=True)
    
    # Application data (stored as JSON)
    personal_info = Column(JSON, nullable=False)
    living_environment = Column(JSON, nullable=False)
    pet_experience = Column(JSON, nullable=False)
    
    # Review information
    review_notes = Column(Text)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    submitted_at = Column(DateTime(timezone=True))
    
    # Relationships
    pet = relationship("Pet", back_populates="adoption_applications")
    applicant = relationship("User", back_populates="adoption_applications", foreign_keys=[applicant_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    chat_room = relationship("ChatRoom", back_populates="application", uselist=False)
    documents = relationship("ApplicationDocument", back_populates="application", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AdoptionApplication(id={self.id}, application_id='{self.application_id}', status='{self.status}')>"
    
    @property
    def is_draft(self) -> bool:
        """Check if application is in draft status"""
        return self.status == ApplicationStatus.DRAFT
    
    @property
    def is_submitted(self) -> bool:
        """Check if application has been submitted"""
        return self.status != ApplicationStatus.DRAFT
    
    @property
    def is_approved(self) -> bool:
        """Check if application is approved"""
        return self.status == ApplicationStatus.APPROVED
    
    @property
    def is_completed(self) -> bool:
        """Check if adoption is completed"""
        return self.status == ApplicationStatus.COMPLETED
    
    @property
    def can_be_edited(self) -> bool:
        """Check if application can still be edited"""
        return self.status in [ApplicationStatus.DRAFT, ApplicationStatus.SUBMITTED]


class ApplicationDocument(Base):
    """Application document model for storing uploaded documents"""
    
    __tablename__ = "application_documents"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Related application
    application_id = Column(Integer, ForeignKey("adoption_applications.id"), nullable=False, index=True)
    
    # Document information
    document_type = Column(String(50), nullable=False)  # e.g., 'id_card', 'income_proof', 'housing_proof'
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_key = Column(String(255), nullable=False)  # S3 key or file identifier
    file_size = Column(Integer)  # File size in bytes
    mime_type = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    application = relationship("AdoptionApplication", back_populates="documents")
    
    def __repr__(self):
        return f"<ApplicationDocument(id={self.id}, type='{self.document_type}', file='{self.file_name}')>"