from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.container import Container
from app.models.ship import Ship
from app.models.port import Port
from app.schemas.container import (
    ContainerCreate, ContainerUpdate, ContainerResponse,
    ContainerLoadRequest, ContainerUnloadRequest, ContainerTransferRequest
)
from app.services.logistics_service import LogisticsService
from app.auth.rbac import port_manager_or_admin, authenticated_user

router = APIRouter(prefix="/api/containers", tags=["Containers"])

@router.get("", response_model=List[ContainerResponse], dependencies=[Depends(authenticated_user)])
def get_containers(
    search: Optional[str] = Query(None),
    type_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Container)
    if search:
        query = query.filter(Container.container_code.ilike(f"%{search}%"))
    if type_filter:
        query = query.filter(Container.type == type_filter)
    return query.all()

@router.post("", response_model=ContainerResponse, dependencies=[Depends(port_manager_or_admin)])
def create_container(c_in: ContainerCreate, db: Session = Depends(get_db)):
    if db.query(Container).filter(Container.container_code == c_in.container_code).first():
        raise HTTPException(status_code=400, detail="Container code must be unique")
    
    status_str = "In Port" if c_in.current_port_id else ("On Ship" if c_in.assigned_ship_id else "In Transit")
    container = Container(
        container_code=c_in.container_code,
        type=c_in.type,
        weight=c_in.weight,
        current_port_id=c_in.current_port_id,
        assigned_ship_id=c_in.assigned_ship_id,
        destination_port_id=c_in.destination_port_id,
        status=status_str
    )
    db.add(container)
    db.commit()
    db.refresh(container)
    return container

@router.post("/{container_id}/load", response_model=ContainerResponse, dependencies=[Depends(port_manager_or_admin)])
def load_container(container_id: int, req: ContainerLoadRequest, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    
    ship = db.query(Ship).filter(Ship.id == req.ship_id).first()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    # Validate cargo capacity & rules via LogisticsService
    try:
        LogisticsService.validate_ship_cargo(ship, container, adding=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    container.assigned_ship_id = ship.id
    container.current_port_id = None
    container.status = "On Ship"

    db.commit()
    db.refresh(container)
    return container

@router.post("/{container_id}/unload", response_model=ContainerResponse, dependencies=[Depends(port_manager_or_admin)])
def unload_container(container_id: int, req: ContainerUnloadRequest, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    
    port = db.query(Port).filter(Port.id == req.port_id).first()
    if not port:
        raise HTTPException(status_code=404, detail="Port not found")
    
    # Port storage capacity check
    if len(port.stored_containers) >= port.available_storage:
        raise HTTPException(status_code=400, detail="Port storage capacity reached.")

    container.assigned_ship_id = None
    container.current_port_id = port.id
    container.status = "In Port"

    db.commit()
    db.refresh(container)
    return container

@router.delete("/{container_id}", dependencies=[Depends(port_manager_or_admin)])
def delete_container(container_id: int, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    db.delete(container)
    db.commit()
    return {"message": "Container deleted successfully"}
