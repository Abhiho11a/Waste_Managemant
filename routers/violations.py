from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.db_models import Violation
from schemas.pydantic_schemas import ViolationReportRequest, ViolationResponse
from middleware.auth_middleware import get_current_user, require_role
from typing import List

router = APIRouter(prefix="/violations", tags=["violations"])

@router.get("/live", response_model=List[ViolationResponse])
async def get_live_violations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Violation).order_by(Violation.timestamp.desc()).limit(50)
    )
    return result.scalars().all()

@router.post("/report", response_model=ViolationResponse, status_code=201)
async def report_violation(
    data: ViolationReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role('enforcement', 'authority', 'fisherman')),
):
    violation = Violation(
        vessel_id=data.vessel_id,
        zone=data.zone,
        violation_type=data.violation_type,
        severity=data.severity,
        blockchain_tx_hash=data.blockchain_tx_hash,
        reported_by=current_user.id,
        latitude=data.latitude,
        longitude=data.longitude,
    )
    db.add(violation)
    await db.commit()
    await db.refresh(violation)
    return violation

@router.get("/{violation_id}", response_model=ViolationResponse)
async def get_violation(violation_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    result = await db.execute(
        select(Violation).where(Violation.id == UUID(violation_id))
    )
    v = result.scalar_one_or_none()
    if not v:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Violation not found")
    return v
