from services.stress_engine import compute_stress_score, get_stress_for_region
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pydantic_schemas import SimulationInput, SimulationResultResponse
from models.db_models import SimulationResult
from datetime import datetime

async def run_policy_simulation(
    input_data: SimulationInput,
    db: AsyncSession
) -> SimulationResultResponse:
    """
    Simulate policy impact on stress score over 5 years.

    Logic:
    - Get current stress index for the region
    - Apply reduction factors based on policy inputs
    - fishing_reduction reduces fish_stock_decline (improves fish_stock_level)
    - plastic_reduction reduces pollution_score
    - zone_protection reduces species_risk and pollution_score
    - Compute projected stress score after 5 years
    - Compute biodiversity_recovery as percent improvement
    """
    # Get current stress for region
    current = await get_stress_for_region(input_data.region, db)

    # Apply policy effects (linear reduction over 5 years)
    factor = lambda reduction, base: max(base - (base * reduction / 100 * 0.7), 0)

    projected_species_risk = factor(input_data.zone_protection * 0.5, current.species_risk)
    projected_fish_stock_level = min(current.fish_stock_level + (input_data.fishing_reduction * 0.6), 100)
    projected_temperature = current.temperature_anomaly  # unaffected by these policies
    projected_pollution = factor(input_data.plastic_reduction + input_data.zone_protection * 0.3, current.pollution_score)

    predicted_score = compute_stress_score(
        projected_species_risk,
        projected_fish_stock_level,
        projected_temperature,
        projected_pollution,
    )

    biodiversity_recovery = round(max(0, (current.score - predicted_score) / current.score * 100), 2)

    # Store result
    result = SimulationResult(
        region=input_data.region,
        input_parameters=input_data.model_dump(),
        predicted_score=predicted_score,
        biodiversity_recovery=biodiversity_recovery,
    )
    db.add(result)
    await db.commit()

    return SimulationResultResponse(
        region=input_data.region,
        input_parameters=input_data.model_dump(),
        predicted_score=predicted_score,
        biodiversity_recovery=biodiversity_recovery,
        timestamp=datetime.utcnow(),
        projection_years=5,
    )
