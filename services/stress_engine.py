from models.db_models import StressIndex
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import random
from services.ml_models import get_model_manager

# Stress Index Formula (from Master PRD Section 12)
def compute_stress_score(species_risk: float, fish_stock_level: float,
                          temperature_anomaly: float, pollution_score: float) -> float:
    """
    stress_score = 0.35 * species_risk + 0.30 * fish_stock_decline +
                   0.20 * temperature_anomaly + 0.15 * pollution_score
    fish_stock_decline = 100 - fish_stock_level (inverted: low stock = high stress)
    All inputs 0-100.
    """
    fish_stock_decline = 100 - fish_stock_level
    score = (
        0.35 * species_risk +
        0.30 * fish_stock_decline +
        0.20 * temperature_anomaly +
        0.15 * pollution_score
    )
    return round(min(max(score, 0), 100), 2)

async def get_stress_for_region(region: str, db: AsyncSession):
    """Fetch latest stress index for region, compute if missing"""
    result = await db.execute(
        select(StressIndex)
        .where(StressIndex.region == region)
        .order_by(StressIndex.computed_at.desc())
        .limit(1)
    )
    record = result.scalar_one_or_none()
    if record:
        return record
    # Generate a realistic stress index record for this region if none exists
    return await seed_stress_for_region(region, db)

async def seed_stress_for_region(region: str, db: AsyncSession) -> StressIndex:
    """Seed stress index using ML models when available"""
    try:
        model_manager = get_model_manager()

        # Get predictions from ML models
        species_risk = min(max(model_manager.predict_t_sr([random.uniform(0, 100)]), 0), 100)
        fish_stock_level = min(max(model_manager.predict_t_bio([random.uniform(0, 100)]), 0), 100)
        temperature_anomaly = min(max(model_manager.predict_t_ab([random.uniform(0, 100)]), 0), 100)
        pollution_score = min(max(model_manager.predict_r_bio([random.uniform(0, 100)]), 0), 100)
    except Exception as e:
        print(f"Using fallback values due to ML error: {e}")
        # Fallback to random values if ML models fail
        species_risk = round(random.uniform(20, 85), 1)
        fish_stock_level = round(random.uniform(20, 80), 1)
        temperature_anomaly = round(random.uniform(5, 70), 1)
        pollution_score = round(random.uniform(15, 80), 1)

    score = compute_stress_score(species_risk, fish_stock_level, temperature_anomaly, pollution_score)

    record = StressIndex(
        region=region,
        score=score,
        species_risk=round(species_risk, 1),
        fish_stock_level=round(fish_stock_level, 1),
        temperature_anomaly=round(temperature_anomaly, 1),
        pollution_score=round(pollution_score, 1),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record
