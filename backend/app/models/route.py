from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    ship_id = Column(Integer, ForeignKey("ships.id"), nullable=False)
    origin_port_id = Column(Integer, ForeignKey("ports.id"), nullable=False)
    destination_port_id = Column(Integer, ForeignKey("ports.id"), nullable=False)
    
    distance = Column(Float, nullable=False)
    estimated_fuel = Column(Float, nullable=False)
    progress = Column(Float, default=0.0) # 0.0 to 100.0 percent
    status = Column(String, default="Pending") # Pending, In Progress, Completed, Cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ship = relationship("Ship")
    origin_port = relationship("Port", foreign_keys=[origin_port_id])
    destination_port = relationship("Port", foreign_keys=[destination_port_id])
