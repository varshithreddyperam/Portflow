from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PortBase(BaseModel):
    name: str
    x_coord: float
    y_coord: float
    dock_capacity: int = Field(default=5, ge=1)
    available_storage: int = Field(default=100, ge=0)

class PortCreate(PortBase):
    pass

class PortUpdate(BaseModel):
    name: Optional[str] = None
    x_coord: Optional[float] = None
    y_coord: Optional[float] = None
    dock_capacity: Optional[int] = None
    available_storage: Optional[int] = None

class PortResponse(PortBase):
    id: int
    docked_ships_count: int = 0
    stored_containers_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
