from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Ship(Base):
    __tablename__ = "ships"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    max_weight = Column(Float, nullable=False, default=1000.0) # in metric tons
    fuel_capacity = Column(Float, nullable=False, default=500.0) # in liters or units
    current_fuel = Column(Float, nullable=False, default=500.0)
    heavy_limit = Column(Integer, nullable=False, default=10)
    refrigerated_limit = Column(Integer, nullable=False, default=10)
    liquid_limit = Column(Integer, nullable=False, default=10)
    
    current_port_id = Column(Integer, ForeignKey("ports.id"), nullable=True)
    destination_port_id = Column(Integer, ForeignKey("ports.id"), nullable=True)
    
    status = Column(String, default="Docked") # Docked, In Transit, Maintenance
    current_x = Column(Float, nullable=True)
    current_y = Column(Float, nullable=True)
    speed = Column(Float, default=1.0) # speed modifier
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    current_port = relationship("Port", foreign_keys=[current_port_id], back_populates="docked_ships")
    destination_port = relationship("Port", foreign_keys=[destination_port_id])
    containers = relationship("Container", foreign_keys="Container.assigned_ship_id", back_populates="assigned_ship")
    fuel_logs = relationship("FuelLog", back_populates="ship", cascade="all, delete-orphan")
    movement_logs = relationship("MovementLog", back_populates="ship", cascade="all, delete-orphan")
