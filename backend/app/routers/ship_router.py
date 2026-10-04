from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.ship import Ship
from app.models.port import Port
from app.models.log import FuelLog, MovementLog
from app.schemas.ship import ShipCreate, ShipUpdate, ShipResponse, ShipRefuelRequest
from app.auth.rbac import fleet_manager_or_admin, authenticated_user

router = APIRouter(prefix="/api/ships", tags=["Ships"])

def format_ship_response(ship: Ship) -> dict:
    containers = list(ship.containers)
    total_weight = sum(c.weight for c in containers)
    heavy = sum(1 for c in containers if c.type == "Heavy")
    refrig = sum(1 for c in containers if c.type == "Refrigerated")
    liquid = sum(1 for c in containers if c.type == "Liquid")
    basic = sum(1 for c in containers if c.type == "Basic")

    return {
        "id": ship.id,
        "name": ship.name,
        "max_weight": ship.max_weight,
        "fuel_capacity": ship.fuel_capacity,
        "current_fuel": ship.current_fuel,
        "heavy_limit": ship.heavy_limit,
        "refrigerated_limit": ship.refrigerated_limit,
        "liquid_limit": ship.liquid_limit,
        "current_port_id": ship.current_port_id,
        "destination_port_id": ship.destination_port_id,
        "status": ship.status,
        "current_x": ship.current_x,
        "current_y": ship.current_y,
        "speed": ship.speed,
        "current_weight": round(total_weight, 2),
        "heavy_count": heavy,
        "refrigerated_count": refrig,
        "liquid_count": liquid,
        "basic_count": basic,
        "created_at": ship.created_at
    }

@router.get("", response_model=List[ShipResponse], dependencies=[Depends(authenticated_user)])
def get_ships(search: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Ship)
    if search:
        query = query.filter(Ship.name.ilike(f"%{search}%"))
    ships = query.all()
    return [format_ship_response(s) for s in ships]

@router.get("/{ship_id}", response_model=ShipResponse, dependencies=[Depends(authenticated_user)])
def get_ship(ship_id: int, db: Session = Depends(get_db)):
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    return format_ship_response(ship)

@router.post("", response_model=ShipResponse, dependencies=[Depends(fleet_manager_or_admin)])
def create_ship(ship_in: ShipCreate, db: Session = Depends(get_db)):
    if db.query(Ship).filter(Ship.name == ship_in.name).first():
        raise HTTPException(status_code=400, detail="Ship with this name already exists")
    
    current_x, current_y = 0.0, 0.0
    if ship_in.current_port_id:
        port = db.query(Port).filter(Port.id == ship_in.current_port_id).first()
        if port:
            current_x, current_y = port.x_coord, port.y_coord

    ship = Ship(
        name=ship_in.name,
        max_weight=ship_in.max_weight,
        fuel_capacity=ship_in.fuel_capacity,
        current_fuel=ship_in.current_fuel if ship_in.current_fuel is not None else ship_in.fuel_capacity,
        heavy_limit=ship_in.heavy_limit,
        refrigerated_limit=ship_in.refrigerated_limit,
        liquid_limit=ship_in.liquid_limit,
        current_port_id=ship_in.current_port_id,
        current_x=current_x,
        current_y=current_y,
        status="Docked" if ship_in.current_port_id else "In Transit"
    )
    db.add(ship)
    db.commit()
    db.refresh(ship)
    return format_ship_response(ship)

@router.put("/{ship_id}", response_model=ShipResponse, dependencies=[Depends(fleet_manager_or_admin)])
def update_ship(ship_id: int, ship_in: ShipUpdate, db: Session = Depends(get_db)):
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    for field, val in ship_in.dict(exclude_unset=True).items():
        setattr(ship, field, val)

    db.commit()
    db.refresh(ship)
    return format_ship_response(ship)

@router.post("/{ship_id}/refuel", response_model=ShipResponse, dependencies=[Depends(fleet_manager_or_admin)])
def refuel_ship(ship_id: int, req: ShipRefuelRequest, db: Session = Depends(get_db)):
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    before = ship.current_fuel
    ship.current_fuel = min(ship.fuel_capacity, ship.current_fuel + req.amount)
    after = ship.current_fuel

    db.add(FuelLog(
        ship_id=ship.id,
        action="Refuel",
        amount=req.amount,
        fuel_before=before,
        fuel_after=after
    ))
    db.commit()
    db.refresh(ship)
    return format_ship_response(ship)

@router.delete("/{ship_id}", dependencies=[Depends(fleet_manager_or_admin)])
def delete_ship(ship_id: int, db: Session = Depends(get_db)):
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    if ship.status == "In Transit":
        raise HTTPException(status_code=400, detail="Cannot delete ship while in transit.")
    
    db.delete(ship)
    db.commit()
    return {"message": "Ship deleted successfully"}
