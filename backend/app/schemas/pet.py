from __future__ import annotations
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel


class PetPhotoSchema(BaseModel):
    id: int
    pet_id: int
    file_url: Optional[str]

    model_config = {"from_attributes": True}


class PetSchema(BaseModel):
    id: int
    name: Optional[str]
    species: Optional[str]
    breed: Optional[str]
    gender: Optional[str]
    age_years: Optional[int]
    age_months: Optional[int]
    size: Optional[str]
    description: Optional[str]
    adoption_fee: Optional[float]
    status: Optional[str]
    primary_photo_url: Optional[str]
    spayed_neutered: Optional[bool]
    vaccination_status: Optional[str]
    good_with_kids: Optional[bool]
    good_with_pets: Optional[bool]
    energy_level: Optional[str]
    location: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PaginationInfo(BaseModel):
    page: int
    limit: int
    total: int
    pages: int


class PaginatedPets(BaseModel):
    items: List[PetSchema]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = {"from_attributes": True}


class PetListResponse(BaseModel):
    """前端期望的格式：{pets: [], pagination: {}}"""
    pets: List[PetSchema]
    pagination: PaginationInfo


class SearchParams(BaseModel):
    page: int = 1
    limit: int = 24
    query: Optional[str] = None
    species: Optional[list[str]] = None
    gender: Optional[str] = None
    size: Optional[list[str]] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    good_with_kids: Optional[bool] = None
    good_with_pets: Optional[bool] = None

    model_config = {"from_attributes": True}
