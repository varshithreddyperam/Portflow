from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.route import Route
from app.models.ship import Ship
from app.models.port import Port
from app.models.log import MovementLog
from app.schemas.route import RouteCreate, RouteResponse, CalculationPreviewResponse
from app.services.logistics_service import LogisticsService
from app.auth.rbac import fleet_manager_or_admin, authenticated_user

router = APIRouter(prefix="/api/routes", tags=["Routes"])

@router.get("", response_model=List[RouteResponse], dependencies=[Depends(authenticated_user)])
def list_routes(db: Session = Depends(get_db)):
    routes = db.query(Route).order_by(Route.id.desc()).all()
    res = []
    for r in routes:
        res.append({
            "id": r.id,
            "ship_id": r.ship_id,
            "ship_name": r.ship.name if r.ship else "Unknown",
            "origin_port_id": r.origin_port_id,
            "origin_port_name": r.origin_port.name if r.origin_port else "Unknown",
            "destination_port_id": r.destination_port_id,
            "destination_port_name": r.destination_port.name if r.destination_port else "Unknown",
            "distance": r.distance,
            "estimated_fuel": r.estimated_fuel,
            "progress": r.progress,
            "status": r.status,
            "created_at": r.created_at
        })
    return res

@router.get("/preview", response_model=CalculationPreviewResponse, dependencies=[Depends(authenticated_user)])
def preview_route(ship_id: int, destination_port_id: int, db: Session = Depends(get_db)):
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    dest_port = db.query(Port).filter(Port.id == destination_port_id).first()
    if not ship or not dest_port:
        raise HTTPException(status_code=404, detail="Ship or Destination Port not found")

    if not ship.current_port_id:
        raise HTTPException(status_code=400, detail="Ship must be docked at a port to plan a route.")

    origin_port = db.query(Port).filter(Port.id == ship.current_port_id).first()
    if origin_port.id == dest_port.id:
        raise HTTPException(status_code=400, detail="Origin and Destination ports must be different.")

    dist = LogisticsService.calculate_distance(origin_port.x_coord, origin_port.y_coord, dest_port.x_coord, dest_port.y_coord)
    req_fuel = LogisticsService.calculate_fuel_consumption(dist, ship.containers)
    total_cargo_weight = sum(c.weight for c in ship.containers)

    return {
        "origin_port": origin_port.name,
        "destination_port": dest_port.name,
        "distance": dist,
        "required_fuel": req_fuel,
        "current_fuel": ship.current_fuel,
        "has_sufficient_fuel": ship.current_fuel >= req_fuel,
        "total_cargo_weight": total_cargo_weight
    }

@router.post("", response_model=RouteResponse, dependencies=[Depends(fleet_manager_or_admin)])
def create_and_dispatch_route(req: RouteCreate, db: Session = Depends(get_db)):
    ship = db.query(Ship).filter(Ship.id == req.ship_id).first()
    dest_port = db.query(Port).filter(Port.id == req.destination_port_id).first()
    if not ship or not dest_port:
        raise HTTPException(status_code=404, detail="Ship or Port not found")

    if ship.status == "In Transit":
        raise HTTPException(status_code=400, detail="Ship is already in transit.")

    if not ship.current_port_id:
        raise HTTPException(status_code=400, detail="Ship must be docked at a port to depart.")

    origin_port = db.query(Port).filter(Port.id == ship.current_port_id).first()
    if origin_port.id == dest_port.id:
        raise HTTPException(status_code=400, detail="Destination port cannot be the same as current port.")

    # Calculate distance & fuel
    dist = LogisticsService.calculate_distance(origin_port.x_coord, origin_port.y_coord, dest_port.x_coord, dest_port.y_coord)
    req_fuel = LogisticsService.calculate_fuel_consumption(dist, ship.containers)

    if ship.current_fuel < req_fuel:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient fuel! Required: {req_fuel} L, Current: {ship.current_fuel} L. Refuel ship first."
        )

    route = Route(
        ship_id=ship.id,
        origin_port_id=origin_port.id,
        destination_port_id=dest_port.id,
        distance=dist,
        estimated_fuel=req_fuel,
        progress=0.0,
        status="In Progress"
    )

    ship.destination_port_id = dest_port.id
    ship.current_port_id = None
    ship.status = "In Transit"

    db.add(MovementLog(
        ship_id=ship.id,
        origin_port_id=origin_port.id,
        destination_port_id=dest_port.id,
        details=f"Ship '{ship.name}' departed from '{origin_port.name}' bound for '{dest_port.name}'."
    ))

    db.add(route)
    db.commit()
    db.refresh(route)

    return {
        "id": route.id,
        "ship_id": ship.id,
        "ship_name": ship.name,
        "origin_port_id": origin_port.id,
        "origin_port_name": origin_port.name,
        "destination_port_id": dest_port.id,
        "destination_port_name": dest_port.name,
        "distance": dist,
        "estimated_fuel": req_fuel,
        "progress": 0.0,
        "status": "In Progress",
        "created_at": route.created_at
    }
