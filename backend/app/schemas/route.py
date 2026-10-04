from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RouteCreate(BaseModel):
    ship_id: int
    destination_port_id: int

class RouteResponse(BaseModel):
    id: int
    ship_id: int
    ship_name: str
    origin_port_id: int
    origin_port_name: str
    destination_port_id: int
    destination_port_name: str
    distance: float
    estimated_fuel: float
    progress: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class CalculationPreviewResponse(BaseModel):
    origin_port: str
    destination_port: str
    distance: float
    required_fuel: float
    current_fuel: float
    has_sufficient_fuel: bool
    total_cargo_weight: float
