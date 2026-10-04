from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
import json
import csv
import io
from typing import Optional
from app.database.session import get_db
from app.models.port import Port
from app.models.ship import Ship
from app.models.container import Container
from app.models.log import FuelLog, MovementLog
from app.auth.rbac import authenticated_user

router = APIRouter(prefix="/api/reports", tags=["Reports & Analytics"])

@router.get("/analytics", dependencies=[Depends(authenticated_user)])
def get_analytics(db: Session = Depends(get_db)):
    ports = db.query(Port).all()
    ships = db.query(Ship).all()
    containers = db.query(Container).all()

    total_ports = len(ports)
    total_ships = len(ships)
    docked_ships = sum(1 for s in ships if s.status == "Docked")
    in_transit_ships = sum(1 for s in ships if s.status == "In Transit")
    total_containers = len(containers)
    total_fuel_consumed = db.query(FuelLog).filter(FuelLog.action.ilike("%consumption%")).all()
    fuel_usage_sum = sum(l.amount for l in total_fuel_consumed)

    # Container type distribution
    type_counts = {
        "Basic": sum(1 for c in containers if c.type == "Basic"),
        "Heavy": sum(1 for c in containers if c.type == "Heavy"),
        "Refrigerated": sum(1 for c in containers if c.type == "Refrigerated"),
        "Liquid": sum(1 for c in containers if c.type == "Liquid")
    }

    # Port utilization
    port_utilization = [
        {
            "name": p.name,
            "dock_capacity": p.dock_capacity,
            "docked_ships": len(p.docked_ships),
            "utilization_pct": round((len(p.docked_ships) / p.dock_capacity * 100.0) if p.dock_capacity > 0 else 0, 1)
        } for p in ports
    ]

    return {
        "summary": {
            "total_ports": total_ports,
            "total_ships": total_ships,
            "docked_ships": docked_ships,
            "in_transit_ships": in_transit_ships,
            "total_containers": total_containers,
            "total_fuel_consumed": round(fuel_usage_sum, 2)
        },
        "container_distribution": type_counts,
        "port_utilization": port_utilization
    }

@router.get("/movement-history", dependencies=[Depends(authenticated_user)])
def get_movement_history(db: Session = Depends(get_db)):
    logs = db.query(MovementLog).order_by(MovementLog.timestamp.desc()).limit(100).all()
    return [
        {
            "id": l.id,
            "ship_name": l.ship.name if l.ship else "Unknown",
            "origin_port": l.origin_port.name if l.origin_port else "N/A",
            "destination_port": l.destination_port.name if l.destination_port else "N/A",
            "details": l.details,
            "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for l in logs
    ]

@router.get("/fuel-logs", dependencies=[Depends(authenticated_user)])
def get_fuel_logs(db: Session = Depends(get_db)):
    logs = db.query(FuelLog).order_by(FuelLog.timestamp.desc()).limit(100).all()
    return [
        {
            "id": l.id,
            "ship_name": l.ship.name if l.ship else "Unknown",
            "action": l.action,
            "amount": l.amount,
            "fuel_before": l.fuel_before,
            "fuel_after": l.fuel_after,
            "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for l in logs
    ]

@router.get("/export/csv", dependencies=[Depends(authenticated_user)])
def export_csv(type: str = Query("ships"), db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)

    if type == "ships":
        ships = db.query(Ship).all()
        writer.writerow(["ID", "Name", "Max Weight", "Fuel Capacity", "Current Fuel", "Status", "Current Port"])
        for s in ships:
            writer.writerow([s.id, s.name, s.max_weight, s.fuel_capacity, s.current_fuel, s.status, s.current_port.name if s.current_port else "In Transit"])
    elif type == "ports":
        ports = db.query(Port).all()
        writer.writerow(["ID", "Name", "X", "Y", "Dock Capacity", "Storage Capacity", "Docked Ships"])
        for p in ports:
            writer.writerow([p.id, p.name, p.x_coord, p.y_coord, p.dock_capacity, p.available_storage, len(p.docked_ships)])
    else:
        containers = db.query(Container).all()
        writer.writerow(["ID", "Code", "Type", "Weight", "Status", "Port", "Ship"])
        for c in containers:
            writer.writerow([c.id, c.container_code, c.type, c.weight, c.status, c.current_port.name if c.current_port else "", c.assigned_ship.name if c.assigned_ship else ""])

    output.seek(0)
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=portflow_{type}.csv"})
