from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    x_coord = Column(Float, nullable=False, default=0.0)
    y_coord = Column(Float, nullable=False, default=0.0)
    dock_capacity = Column(Integer, nullable=False, default=5)
    available_storage = Column(Integer, nullable=False, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    docked_ships = relationship("Ship", foreign_keys="Ship.current_port_id", back_populates="current_port")
    stored_containers = relationship("Container", foreign_keys="Container.current_port_id", back_populates="current_port")
