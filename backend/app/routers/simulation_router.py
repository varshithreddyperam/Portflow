from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.simulation import SimulationControlRequest, SimulationStatusResponse
from app.simulation.engine import simulation_engine
from app.simulation.websocket_manager import ws_manager
from app.models.ship import Ship
from app.models.container import Container
from app.auth.rbac import admin_only, authenticated_user

router = APIRouter(prefix="/api/simulation", tags=["Simulation Engine"])

@router.get("/status", response_model=SimulationStatusResponse, dependencies=[Depends(authenticated_user)])
def get_simulation_status(db: Session = Depends(get_db)):
    state = simulation_engine.get_state(db)
    active_ships = db.query(Ship).count()
    in_transit = db.query(Ship).filter(Ship.status == "In Transit").count()
    containers_count = db.query(Container).count()

    return {
        "status": state.status,
        "speed_multiplier": state.speed_multiplier,
        "ticks_elapsed": state.ticks_elapsed,
        "active_ships_count": active_ships,
        "ships_in_transit_count": in_transit,
        "total_containers_count": containers_count,
        "last_tick_time": state.last_tick_time
    }

@router.post("/control", dependencies=[Depends(admin_only)])
async def control_simulation(req: SimulationControlRequest, db: Session = Depends(get_db)):
    state = simulation_engine.get_state(db)
    if req.speed_multiplier and req.speed_multiplier > 0:
        state.speed_multiplier = req.speed_multiplier
        db.commit()

    action = req.action.lower()
    if action == "start":
        await simulation_engine.start()
    elif action == "pause":
        await simulation_engine.pause()
    elif action == "resume":
        await simulation_engine.resume()
    elif action == "stop":
        await simulation_engine.stop()
    elif action == "reset":
        await simulation_engine.reset()
    else:
        raise HTTPException(status_code=400, detail="Invalid action parameter")

    return {"message": f"Simulation action '{action}' executed successfully"}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep socket alive and receive client ping messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
