from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ShipBase(BaseModel):
    name: str
    max_weight: float = Field(default=1000.0, gt=0)
    fuel_capacity: float = Field(default=500.0, gt=0)
    heavy_limit: int = Field(default=10, ge=0)
    refrigerated_limit: int = Field(default=10, ge=0)
    liquid_limit: int = Field(default=10, ge=0)
    current_port_id: Optional[int] = None

class ShipCreate(ShipBase):
    current_fuel: Optional[float] = None

class ShipUpdate(BaseModel):
    name: Optional[str] = None
    max_weight: Optional[float] = None
    fuel_capacity: Optional[float] = None
    heavy_limit: Optional[int] = None
    refrigerated_limit: Optional[int] = None
    liquid_limit: Optional[int] = None
    status: Optional[str] = None

class ShipRefuelRequest(BaseModel):
    amount: float = Field(gt=0)

class ShipMoveRequest(BaseModel):
    destination_port_id: int

class ShipResponse(ShipBase):
    id: int
    current_fuel: float
    destination_port_id: Optional[int] = None
    status: str
    current_x: Optional[float] = None
    current_y: Optional[float] = None
    speed: float
    current_weight: float = 0.0
    heavy_count: int = 0
    refrigerated_count: int = 0
    liquid_count: int = 0
    basic_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
