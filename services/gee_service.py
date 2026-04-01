import random
from datetime import datetime, timedelta
from typing import Any

# Ocean regions with their approximate bounding boxes [min_lat, max_lat, min_lng, max_lng]
OCEAN_REGIONS = {
    "Bay of Bengal": (5, 22, 80, 100),
    "Arabian Sea": (8, 25, 55, 75),
    "South China Sea": (5, 22, 108, 122),
    "Gulf of Mexico": (18, 30, -98, -80),
    "North Sea": (51, 60, -2, 8),
    "Mediterranean Sea": (30, 46, -5, 37),
    "Coral Triangle": (-10, 5, 115, 135),
    "Great Barrier Reef": (-24, -12, 142, 155),
}

POLLUTION_TYPES = ["oil_spill", "plastic", "algal_bloom", "chemical_runoff", "vessel_cluster"]

def _random_coord(region: str) -> tuple[float, float]:
    bbox = OCEAN_REGIONS[region]
    lat = random.uniform(bbox[0], bbox[1])
    lng = random.uniform(bbox[2], bbox[3])
    return lat, lng

def _random_time() -> str:
    days_ago = random.randint(0, 30)
    dt = datetime.utcnow() - timedelta(days=days_ago)
    return dt.isoformat() + "Z"

async def get_pollution_heatmap() -> dict:
    """Generate mock pollution GeoJSON with 40 realistic events"""
    features = []
    for _ in range(40):
        region = random.choice(list(OCEAN_REGIONS.keys()))
        lat, lng = _random_coord(region)
        pollution_type = random.choice(POLLUTION_TYPES)
        severity = round(random.uniform(10, 95), 1)

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lng, lat]},
            "properties": {
                "id": f"pe_{random.randint(10000, 99999)}",
                "pollution_type": pollution_type,
                "severity_score": severity,
                "timestamp": _random_time(),
                "source": "satellite",
                "region": region,
            }
        })

    return {"type": "FeatureCollection", "features": features}

async def get_algal_bloom_zones() -> dict:
    """Generate mock algal bloom GeoJSON"""
    features = []
    bloom_regions = ["Bay of Bengal", "Gulf of Mexico", "Mediterranean Sea", "Great Barrier Reef"]
    for region in bloom_regions:
        lat, lng = _random_coord(region)
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lng, lat]},
            "properties": {
                "id": f"ab_{random.randint(1000, 9999)}",
                "pollution_type": "algal_bloom",
                "severity_score": round(random.uniform(40, 90), 1),
                "timestamp": _random_time(),
                "source": "satellite",
                "region": region,
                "chlorophyll_concentration": round(random.uniform(5, 50), 2),
            }
        })
    return {"type": "FeatureCollection", "features": features}

async def get_vessel_intrusions() -> list[dict]:
    """Generate mock vessel intrusion events"""
    vessel_ids = [f"VESSEL-{i:04d}" for i in range(1, 20)]
    protected_zones = ["Marine Reserve A", "Protected Reef B", "Sanctuary Zone C", "No-Fish Zone D"]

    intrusions = []
    for _ in range(15):
        region = random.choice(list(OCEAN_REGIONS.keys()))
        lat, lng = _random_coord(region)
        intrusions.append({
            "id": f"vi_{random.randint(10000, 99999)}",
            "vessel_id": random.choice(vessel_ids),
            "zone": random.choice(protected_zones),
            "violation_type": "zone_intrusion",
            "timestamp": _random_time(),
            "severity": random.choice(["low", "medium", "high"]),
            "latitude": lat,
            "longitude": lng,
            "region": region,
            "blockchain_tx_hash": None,
        })
    return intrusions
