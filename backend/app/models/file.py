"""
File model for managing uploaded files and documents
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class FileType(str, enum.Enum):
    """File type enumeration"""
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    OTHER = "other"


class FileStatus(str, enum.Enum):
    """File status enumeration"""
    ACTIVE = "active"
    DELETED = "deleted"
    ARCHIVED = "archived"


class File(Base):
    """File storage records"""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)  # S3 key or local path
    file_url = Column(String(1000), nullable=True)  # Public URL
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    file_type = Column(Enum(FileType), nullable=False, index=True)
    
    # Metadata
    width = Column(Integer, nullable=True)  # For images/videos
    height = Column(Integer, nullable=True)  # For images/videos
    duration = Column(Integer, nullable=True)  # For videos (seconds)
    
    # Ownership and status
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(Enum(FileStatus), default=FileStatus.ACTIVE, nullable=False, index=True)
    
    # References (optional - for linking to specific entities)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=True, index=True)
    application_id = Column(Integer, ForeignKey("adoption_applications.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    uploader = relationship("User", foreign_keys=[uploaded_by])
    pet = relationship("Pet", foreign_keys=[pet_id])
    application = relationship("AdoptionApplication", foreign_keys=[application_id])

    def __repr__(self):
        return f"<File(id={self.id}, filename={self.original_filename}, type={self.file_type})>"
