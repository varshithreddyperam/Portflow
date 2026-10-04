from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SimulationControlRequest(BaseModel):
    action: str # start, pause, resume, stop, reset
    speed_multiplier: Optional[float] = 1.0

class SimulationStatusResponse(BaseModel):
    status: str
    speed_multiplier: float
    ticks_elapsed: int
    active_ships_count: int
    ships_in_transit_count: int
    total_containers_count: int
    last_tick_time: datetime
