from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class FuelLog(Base):
    __tablename__ = "fuel_logs"

    id = Column(Integer, primary_key=True, index=True)
    ship_id = Column(Integer, ForeignKey("ships.id"), nullable=False)
    action = Column(String, nullable=False) # Refuel, Consumption
    amount = Column(Float, nullable=False)
    fuel_before = Column(Float, nullable=False)
    fuel_after = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    ship = relationship("Ship", back_populates="fuel_logs")

class MovementLog(Base):
    __tablename__ = "movement_logs"

    id = Column(Integer, primary_key=True, index=True)
    ship_id = Column(Integer, ForeignKey("ships.id"), nullable=False)
    origin_port_id = Column(Integer, ForeignKey("ports.id"), nullable=True)
    destination_port_id = Column(Integer, ForeignKey("ports.id"), nullable=True)
    details = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    ship = relationship("Ship", back_populates="movement_logs")
    origin_port = relationship("Port", foreign_keys=[origin_port_id])
    destination_port = relationship("Port", foreign_keys=[destination_port_id])

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False) # Port, Ship, Container, Route, System
    entity_id = Column(String, nullable=True)
    details = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
