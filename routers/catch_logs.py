from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.elements import WKTElement
from db.database import get_db
from models.db_models import CatchLog
from schemas.pydantic_schemas import CatchLogRequest, CatchLogResponse
from middleware.auth_middleware import get_current_user
from typing import List
from uuid import UUID

router = APIRouter(prefix="/catch-log", tags=["catch-logs"])

@router.post("", response_model=CatchLogResponse, status_code=201)
async def submit_catch_log(
    data: CatchLogRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    location = None
    if data.latitude and data.longitude:
        location = WKTElement(f"POINT({data.longitude} {data.latitude})", srid=4326)

    log = CatchLog(
        fisherman_id=current_user.id,
        species=data.species,
        quantity=data.quantity,
        location=location,
        tx_hash=data.tx_hash,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)

    return CatchLogResponse(
        id=log.id,
        fisherman_id=log.fisherman_id,
        species=log.species,
        quantity=log.quantity,
        location={"lat": data.latitude, "lng": data.longitude} if data.latitude else None,
        timestamp=log.timestamp,
        tx_hash=log.tx_hash,
        verified=log.verified,
    )

@router.get("/{user_id}", response_model=List[CatchLogResponse])
async def get_catch_logs(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(CatchLog)
        .where(CatchLog.fisherman_id == UUID(user_id))
        .order_by(CatchLog.timestamp.desc())
    )
    logs = result.scalars().all()
    return [
        CatchLogResponse(
            id=log.id, fisherman_id=log.fisherman_id, species=log.species,
            quantity=log.quantity, location=None, timestamp=log.timestamp,
            tx_hash=log.tx_hash, verified=log.verified,
        )
        for log in logs
    ]
