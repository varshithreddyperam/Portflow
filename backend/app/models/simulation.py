from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database.session import Base

class SimulationState(Base):
    __tablename__ = "simulation_state"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="Stopped") # Stopped, Running, Paused
    speed_multiplier = Column(Float, default=1.0)
    ticks_elapsed = Column(Integer, default=0)
    last_tick_time = Column(DateTime, default=datetime.utcnow)
