from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.db_models import StressIndex
from schemas.pydantic_schemas import StressIndexResponse
from services.stress_engine import get_stress_for_region, seed_stress_for_region
from typing import List

VALID_REGIONS = [
    "Bay of Bengal", "Arabian Sea", "South China Sea", "Gulf of Mexico",
    "North Sea", "Mediterranean Sea", "Coral Triangle", "Great Barrier Reef",
]

router = APIRouter(prefix="/stress-index", tags=["stress-index"])

@router.get("/all", response_model=List[StressIndexResponse])
async def get_all_stress_indexes(db: AsyncSession = Depends(get_db)):
    records = []
    for region in VALID_REGIONS:
        record = await get_stress_for_region(region, db)
        records.append(record)
    return records

@router.get("/{region}", response_model=StressIndexResponse)
async def get_stress_index(region: str, db: AsyncSession = Depends(get_db)):
    if region not in VALID_REGIONS:
        raise HTTPException(status_code=404, detail=f"Region '{region}' not found")
    record = await get_stress_for_region(region, db)
    return record
