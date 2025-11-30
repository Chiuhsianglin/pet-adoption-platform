"""
Vaccination record model for tracking pet vaccination history
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, date

from app.database import Base


class VaccinationRecord(Base):
    """Vaccination records for pets"""
    __tablename__ = "vaccination_records"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    vaccine_name = Column(String(100), nullable=False)
    vaccine_type = Column(String(50), nullable=False)  # e.g., "rabies", "distemper", "parvovirus"
    vaccination_date = Column(Date, nullable=False)
    next_due_date = Column(Date, nullable=True)
    veterinarian_name = Column(String(100), nullable=True)
    clinic_name = Column(String(200), nullable=True)
    batch_number = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    pet = relationship("Pet", back_populates="vaccination_records")

    def __repr__(self):
        return f"<VaccinationRecord(id={self.id}, pet_id={self.pet_id}, vaccine={self.vaccine_name}, date={self.vaccination_date})>"
