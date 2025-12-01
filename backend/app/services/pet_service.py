from typing import Tuple, List, Dict, Any, Optional
from math import ceil
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pet import Pet, PetPhoto, PetStatus, PetSpecies, PetGender, PetSize, EnergyLevel


async def list_pets(session: AsyncSession, page: int = 1, limit: int = 24) -> Tuple[List[Pet], int]:
    skip = (page - 1) * limit
    base_query = select(Pet).options(
        selectinload(Pet.photos),
        selectinload(Pet.shelter)
    ).where(Pet.status == PetStatus.AVAILABLE)
    count_q = select(func.count()).select_from(Pet).where(Pet.status == PetStatus.AVAILABLE)

    total_result = await session.execute(count_q)
    total = int(total_result.scalar() or 0)

    result = await session.execute(base_query.offset(skip).limit(limit))
    pets = result.scalars().all()
    return pets, total


async def get_pet_by_id(session: AsyncSession, pet_id: int) -> Optional[Pet]:
    q = select(Pet).options(
        selectinload(Pet.photos),
        selectinload(Pet.shelter)
    ).where(Pet.id == pet_id)
    res = await session.execute(q)
    return res.scalar_one_or_none()


async def search_pets(session: AsyncSession, payload: Dict[str, Any]) -> Dict[str, Any]:
    page = int(payload.get("page", 1))
    limit = int(payload.get("limit", 24))
    skip = (page - 1) * limit

    filters = []
    filters.append(Pet.status == PetStatus.AVAILABLE)

    q = payload.get("query") or payload.get("search")
    if q:
        filters.append(Pet.name.ilike(f"%{q}%"))

    if payload.get("species"):
        vals = payload.get("species")
        if isinstance(vals, list):
            filters.append(Pet.species.in_(vals))
        else:
            filters.append(Pet.species == vals)

    if payload.get("gender"):
        filters.append(Pet.gender == payload.get("gender"))

    if payload.get("size"):
        vals = payload.get("size")
        if isinstance(vals, list):
            filters.append(Pet.size.in_(vals))
        else:
            filters.append(Pet.size == vals)

    # 年龄筛选：age_years 和 age_months 存储的是出生年月，需要计算实际年龄
    # 计算出生日期对应的年龄范围
    from datetime import datetime
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    if payload.get("min_age") is not None:
        try:
            min_age = int(payload.get("min_age"))
            # 最小年龄：宠物出生年份不能晚于 (当前年份 - 最小年龄)
            # 例如：最小年龄 6 岁，当前 2025 年，则出生年份 <= 2019
            max_birth_year = current_year - min_age
            # 考虑月份：如果出生年份等于最大出生年份，月份必须 <= 当前月份
            # 但为了简化，我们用更宽松的条件
            filters.append(Pet.age_years <= max_birth_year)
        except Exception:
            pass

    if payload.get("max_age") is not None:
        try:
            max_age = int(payload.get("max_age"))
            # 最大年龄：宠物出生年份不能早于 (当前年份 - 最大年龄)
            # 例如：最大年龄 20 岁，当前 2025 年，则出生年份 >= 2005
            min_birth_year = current_year - max_age
            filters.append(Pet.age_years >= min_birth_year)
        except Exception:
            pass

    if payload.get("good_with_kids"):
        filters.append(Pet.good_with_kids == True)

    if payload.get("good_with_pets"):
        filters.append(Pet.good_with_pets == True)

    base_query = select(Pet).options(
        selectinload(Pet.photos),
        selectinload(Pet.shelter)
    ).where(and_(*filters))
    count_query = select(func.count()).select_from(Pet).where(and_(*filters))

    # Apply sorting
    sort_by = payload.get("sort_by", "random")
    order = payload.get("order", "desc")
    
    if sort_by == "random":
        # Random order using database random function
        from sqlalchemy import func as sql_func
        base_query = base_query.order_by(sql_func.random())
    else:
        if sort_by == "created_at":
            sort_column = Pet.id  # Use ID for newest (auto-incrementing)
        elif sort_by == "age":
            sort_column = Pet.age_years
        elif sort_by == "name":
            sort_column = Pet.name
        else:
            sort_column = Pet.id  # default
        
        if order == "asc":
            base_query = base_query.order_by(sort_column.asc())
        else:
            base_query = base_query.order_by(sort_column.desc())

    total_result = await session.execute(count_query)
    total = int(total_result.scalar() or 0)

    result = await session.execute(base_query.offset(skip).limit(limit))
    pets = result.scalars().all()

    total_pages = ceil(total / limit) if limit else 1

    return {
        "results": pets,
        "total": total,
        "page": page,
        "page_size": limit,
        "total_pages": total_pages,
        "applied_filters": payload,
    }


async def get_filter_options(session: AsyncSession) -> Dict[str, Any]:
    """Get filter options with counts using efficient group by queries"""
    options = {"species": [], "genders": [], "sizes": [], "energy_levels": []}

    # Species counts (single query with group by)
    species_query = select(Pet.species, func.count(Pet.id)).where(
        Pet.status == PetStatus.AVAILABLE
    ).group_by(Pet.species)
    species_result = await session.execute(species_query)
    species_counts = {row[0]: row[1] for row in species_result if row[0]}
    
    for s in PetSpecies:
        options["species"].append({
            "value": s.value, 
            "label": s.value, 
            "count": species_counts.get(s, 0)
        })

    # Gender counts (single query with group by)
    gender_query = select(Pet.gender, func.count(Pet.id)).where(
        Pet.status == PetStatus.AVAILABLE
    ).group_by(Pet.gender)
    gender_result = await session.execute(gender_query)
    gender_counts = {row[0]: row[1] for row in gender_result if row[0]}
    
    for g in PetGender:
        options["genders"].append({
            "value": g.value, 
            "label": g.value, 
            "count": gender_counts.get(g, 0)
        })

    # Size counts (single query with group by)
    size_query = select(Pet.size, func.count(Pet.id)).where(
        Pet.status == PetStatus.AVAILABLE
    ).group_by(Pet.size)
    size_result = await session.execute(size_query)
    size_counts = {row[0]: row[1] for row in size_result if row[0]}
    
    for sz in PetSize:
        options["sizes"].append({
            "value": sz.value, 
            "label": sz.value, 
            "count": size_counts.get(sz, 0)
        })

    # Energy level counts (single query with group by)
    energy_query = select(Pet.energy_level, func.count(Pet.id)).where(
        Pet.status == PetStatus.AVAILABLE
    ).group_by(Pet.energy_level)
    energy_result = await session.execute(energy_query)
    energy_counts = {row[0]: row[1] for row in energy_result if row[0]}
    
    for e in EnergyLevel:
        options["energy_levels"].append({
            "value": e.value, 
            "label": e.value, 
            "count": energy_counts.get(e, 0)
        })

    return options
