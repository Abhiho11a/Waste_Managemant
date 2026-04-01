from fastapi import APIRouter
from services.gee_service import get_pollution_heatmap, get_algal_bloom_zones, get_vessel_intrusions

router = APIRouter(prefix="/satellite", tags=["satellite"])

@router.get("/pollution-map")
async def pollution_map():
    """Returns GeoJSON FeatureCollection of pollution events"""
    return await get_pollution_heatmap()

@router.get("/algal-bloom")
async def algal_bloom():
    """Returns GeoJSON of algal bloom zones"""
    return await get_algal_bloom_zones()

@router.get("/vessel-intrusions")
async def vessel_intrusions():
    """Returns list of recent vessel intrusion events"""
    return await get_vessel_intrusions()
