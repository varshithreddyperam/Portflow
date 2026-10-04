from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ContainerBase(BaseModel):
    container_code: str
    type: str = "Basic" # Basic, Heavy, Refrigerated, Liquid
    weight: float = Field(default=10.0, gt=0)
    current_port_id: Optional[int] = None
    assigned_ship_id: Optional[int] = None
    destination_port_id: Optional[int] = None

class ContainerCreate(ContainerBase):
    pass

class ContainerUpdate(BaseModel):
    type: Optional[str] = None
    weight: Optional[float] = None
    current_port_id: Optional[int] = None
    assigned_ship_id: Optional[int] = None
    destination_port_id: Optional[int] = None

class ContainerLoadRequest(BaseModel):
    ship_id: int

class ContainerUnloadRequest(BaseModel):
    port_id: int

class ContainerTransferRequest(BaseModel):
    target_ship_id: Optional[int] = None
    target_port_id: Optional[int] = None

class ContainerResponse(ContainerBase):
    id: int
    status: str
    arrival_date: datetime

    class Config:
        from_attributes = True
