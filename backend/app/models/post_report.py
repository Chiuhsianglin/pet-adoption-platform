"""
Post Report model for community feature
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class PostReport(Base):
    """Post report model for tracking user reports on posts"""
    
    __tablename__ = "post_reports"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    post_id = Column(Integer, ForeignKey("community_posts.id"), nullable=False, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Report content
    reason = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    post = relationship("CommunityPost", back_populates="reports")
    reporter = relationship("User", foreign_keys=[reporter_id])
    
    def __repr__(self):
        return f"<PostReport(id={self.id}, post_id={self.post_id}, reporter_id={self.reporter_id})>"
