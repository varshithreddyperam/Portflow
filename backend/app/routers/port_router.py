from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.port import Port
from app.schemas.port import PortCreate, PortUpdate, PortResponse
from app.auth.rbac import port_manager_or_admin, authenticated_user

router = APIRouter(prefix="/api/ports", tags=["Ports"])

@router.get("", response_model=List[PortResponse], dependencies=[Depends(authenticated_user)])
def get_ports(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Port)
    if search:
        query = query.filter(Port.name.ilike(f"%{search}%"))
    ports = query.all()
    
    res = []
    for p in ports:
        port_dict = {
            "id": p.id,
            "name": p.name,
            "x_coord": p.x_coord,
            "y_coord": p.y_coord,
            "dock_capacity": p.dock_capacity,
            "available_storage": p.available_storage,
            "docked_ships_count": len(p.docked_ships),
            "stored_containers_count": len(p.stored_containers),
            "created_at": p.created_at
        }
        res.append(port_dict)
    return res

@router.get("/{port_id}", response_model=PortResponse, dependencies=[Depends(authenticated_user)])
def get_port(port_id: int, db: Session = Depends(get_db)):
    p = db.query(Port).filter(Port.id == port_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Port not found")
    return {
        "id": p.id,
        "name": p.name,
        "x_coord": p.x_coord,
        "y_coord": p.y_coord,
        "dock_capacity": p.dock_capacity,
        "available_storage": p.available_storage,
        "docked_ships_count": len(p.docked_ships),
        "stored_containers_count": len(p.stored_containers),
        "created_at": p.created_at
    }

@router.post("", response_model=PortResponse, dependencies=[Depends(port_manager_or_admin)])
def create_port(port_in: PortCreate, db: Session = Depends(get_db)):
    if db.query(Port).filter(Port.name == port_in.name).first():
        raise HTTPException(status_code=400, detail="Port with this name already exists")
    
    port = Port(**port_in.dict())
    db.add(port)
    db.commit()
    db.refresh(port)
    return {
        "id": port.id,
        "name": port.name,
        "x_coord": port.x_coord,
        "y_coord": port.y_coord,
        "dock_capacity": port.dock_capacity,
        "available_storage": port.available_storage,
        "docked_ships_count": 0,
        "stored_containers_count": 0,
        "created_at": port.created_at
    }

@router.put("/{port_id}", response_model=PortResponse, dependencies=[Depends(port_manager_or_admin)])
def update_port(port_id: int, port_in: PortUpdate, db: Session = Depends(get_db)):
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(status_code=404, detail="Port not found")
    
    for field, val in port_in.dict(exclude_unset=True).items():
        setattr(port, field, val)

    db.commit()
    db.refresh(port)
    return {
        "id": port.id,
        "name": port.name,
        "x_coord": port.x_coord,
        "y_coord": port.y_coord,
        "dock_capacity": port.dock_capacity,
        "available_storage": port.available_storage,
        "docked_ships_count": len(port.docked_ships),
        "stored_containers_count": len(port.stored_containers),
        "created_at": port.created_at
    }

@router.delete("/{port_id}", dependencies=[Depends(port_manager_or_admin)])
def delete_port(port_id: int, db: Session = Depends(get_db)):
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(status_code=404, detail="Port not found")
    if len(port.docked_ships) > 0:
        raise HTTPException(status_code=400, detail="Cannot delete port while ships are docked.")
    
    db.delete(port)
    db.commit()
    return {"message": "Port deleted successfully"}
