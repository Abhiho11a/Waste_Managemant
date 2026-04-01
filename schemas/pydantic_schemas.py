from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

# --- Auth ---
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal['authority', 'enforcement', 'ngo', 'fisherman']

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    wallet_address: Optional[str] = None
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- Pollution ---
class PollutionEventResponse(BaseModel):
    id: UUID
    location: dict  # { lat: float, lng: float }
    pollution_type: str
    severity_score: float
    timestamp: datetime
    source: str
    region: Optional[str] = None
    class Config:
        from_attributes = True

# --- Stress Index ---
class StressIndexResponse(BaseModel):
    id: UUID
    region: str
    score: float
    species_risk: float
    fish_stock_level: float
    temperature_anomaly: float
    pollution_score: float
    computed_at: datetime
    class Config:
        from_attributes = True

# --- Simulation ---
class SimulationInput(BaseModel):
    region: str
    fishing_reduction: float   # 0-100
    plastic_reduction: float   # 0-100
    zone_protection: float     # 0-100

class SimulationResultResponse(BaseModel):
    region: str
    input_parameters: dict
    predicted_score: float
    biodiversity_recovery: float
    timestamp: datetime
    projection_years: int = 5

# --- Violations ---
class ViolationReportRequest(BaseModel):
    vessel_id: str
    zone: str
    violation_type: Literal['quota_exceeded', 'zone_intrusion', 'illegal_fishing']
    severity: Literal['low', 'medium', 'high'] = 'medium'
    blockchain_tx_hash: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ViolationResponse(BaseModel):
    id: UUID
    vessel_id: str
    zone: str
    violation_type: str
    timestamp: datetime
    blockchain_tx_hash: Optional[str] = None
    severity: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    class Config:
        from_attributes = True

# --- Catch Logs ---
class CatchLogRequest(BaseModel):
    species: str
    quantity: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    tx_hash: Optional[str] = None

class CatchLogResponse(BaseModel):
    id: UUID
    fisherman_id: UUID
    species: str
    quantity: float
    location: Optional[dict] = None
    timestamp: datetime
    tx_hash: Optional[str] = None
    verified: bool
    class Config:
        from_attributes = True

