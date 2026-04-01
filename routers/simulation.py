from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.db_models import SimulationResult
from schemas.pydantic_schemas import SimulationInput, SimulationResultResponse
from services.simulation_engine import run_policy_simulation
from middleware.auth_middleware import get_current_user
from typing import List

router = APIRouter(prefix="/simulate", tags=["simulation"])

@router.post("/policy-impact", response_model=SimulationResultResponse)
async def simulate_policy(
    input_data: SimulationInput,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await run_policy_simulation(input_data, db)

@router.get("/results/{region}", response_model=List[SimulationResultResponse])
async def get_simulation_results(
    region: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(SimulationResult)
        .where(SimulationResult.region == region)
        .order_by(SimulationResult.timestamp.desc())
        .limit(10)
    )
    return result.scalars().all()
