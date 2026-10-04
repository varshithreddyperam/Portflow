from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    container_code = Column(String, unique=True, index=True, nullable=False) # e.g. CONT-1001
    type = Column(String, nullable=False, default="Basic") # Basic, Heavy, Refrigerated, Liquid
    weight = Column(Float, nullable=False, default=10.0) # in metric tons
    status = Column(String, default="In Port") # In Port, On Ship, In Transit, Delivered
    
    current_port_id = Column(Integer, ForeignKey("ports.id"), nullable=True)
    assigned_ship_id = Column(Integer, ForeignKey("ships.id"), nullable=True)
    destination_port_id = Column(Integer, ForeignKey("ports.id"), nullable=True)
    
    arrival_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    current_port = relationship("Port", foreign_keys=[current_port_id], back_populates="stored_containers")
    assigned_ship = relationship("Ship", foreign_keys=[assigned_ship_id], back_populates="containers")
    destination_port = relationship("Port", foreign_keys=[destination_port_id])
