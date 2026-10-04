import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.ship import Ship
from app.models.port import Port
from app.models.route import Route
from app.models.log import FuelLog, MovementLog, AuditLog
from app.models.simulation import SimulationState
from app.services.logistics_service import LogisticsService
from app.simulation.websocket_manager import ws_manager

logger = logging.getLogger("simulation")

class SimulationEngine:
    def __init__(self):
        self.is_running = False
        self.task: asyncio.Task = None

    def get_state(self, db: Session) -> SimulationState:
        state = db.query(SimulationState).first()
        if not state:
            state = SimulationState(status="Stopped", speed_multiplier=1.0, ticks_elapsed=0)
            db.add(state)
            db.commit()
            db.refresh(state)
        return state

    async def start(self):
        db = SessionLocal()
        try:
            state = self.get_state(db)
            state.status = "Running"
            db.commit()
            self.is_running = True
            if not self.task or self.task.done():
                self.task = asyncio.create_task(self.run_loop())
            await ws_manager.broadcast({"type": "EVENT", "message": "Simulation started."})
        finally:
            db.close()

    async def pause(self):
        db = SessionLocal()
        try:
            state = self.get_state(db)
            state.status = "Paused"
            db.commit()
            self.is_running = False
            await ws_manager.broadcast({"type": "EVENT", "message": "Simulation paused."})
        finally:
            db.close()

    async def resume(self):
        await self.start()

    async def stop(self):
        db = SessionLocal()
        try:
            state = self.get_state(db)
            state.status = "Stopped"
            db.commit()
            self.is_running = False
            if self.task and not self.task.done():
                self.task.cancel()
            await ws_manager.broadcast({"type": "EVENT", "message": "Simulation stopped."})
        finally:
            db.close()

    async def reset(self):
        db = SessionLocal()
        try:
            state = self.get_state(db)
            state.status = "Stopped"
            state.ticks_elapsed = 0
            # Reset ship locations to their current port coordinates
            in_transit_ships = db.query(Ship).filter(Ship.status == "In Transit").all()
            for ship in in_transit_ships:
                if ship.current_port_id:
                    port = db.query(Port).filter(Port.id == ship.current_port_id).first()
                    if port:
                        ship.current_x = port.x_coord
                        ship.current_y = port.y_coord
                ship.status = "Docked"
                ship.destination_port_id = None

            # Mark routes completed/cancelled
            db.query(Route).filter(Route.status == "In Progress").update({"status": "Cancelled"})
            db.commit()
            self.is_running = False
            await ws_manager.broadcast({"type": "EVENT", "message": "Simulation state reset."})
        finally:
            db.close()

    async def run_loop(self):
        while self.is_running:
            db = SessionLocal()
            try:
                state = self.get_state(db)
                if state.status != "Running":
                    self.is_running = False
                    break

                state.ticks_elapsed += 1
                state.last_tick_time = datetime.utcnow()
                
                # Advance all ships in transit
                in_progress_routes = db.query(Route).filter(Route.status == "In Progress").all()
                for route in in_progress_routes:
                    ship = route.ship
                    dest_port = route.destination_port
                    if not ship or not dest_port:
                        continue

                    # Move ship closer to destination
                    speed = ship.speed * state.speed_multiplier * 5.0 # step size
                    dx = dest_port.x_coord - ship.current_x
                    dy = dest_port.y_coord - ship.current_y
                    dist_remaining = LogisticsService.calculate_distance(ship.current_x, ship.current_y, dest_port.x_coord, dest_port.y_coord)

                    # Calculate fuel step consumption
                    step_fuel = LogisticsService.calculate_fuel_consumption(min(speed, dist_remaining), ship.containers)
                    
                    if ship.current_fuel < step_fuel:
                        # Low fuel warning / Emergency stop
                        ship.status = "Maintenance"
                        route.status = "Cancelled"
                        db.add(FuelLog(
                            ship_id=ship.id,
                            action="Consumption Emergency",
                            amount=0,
                            fuel_before=ship.current_fuel,
                            fuel_after=ship.current_fuel
                        ))
                        db.add(MovementLog(
                            ship_id=ship.id,
                            origin_port_id=route.origin_port_id,
                            destination_port_id=route.destination_port_id,
                            details=f"Ship {ship.name} ran out of fuel during transit!"
                        ))
                        await ws_manager.broadcast({
                            "type": "NOTIFICATION",
                            "level": "danger",
                            "message": f"WARNING: Ship '{ship.name}' ran out of fuel!"
                        })
                        continue

                    ship.current_fuel = round(ship.current_fuel - step_fuel, 2)

                    if dist_remaining <= speed or dist_remaining < 1.0:
                        # Ship arrived at destination port
                        ship.current_x = dest_port.x_coord
                        ship.current_y = dest_port.y_coord
                        ship.current_port_id = dest_port.id
                        ship.destination_port_id = None
                        ship.status = "Docked"
                        route.progress = 100.0
                        route.status = "Completed"

                        # Update container locations
                        for c in ship.containers:
                            c.current_port_id = dest_port.id
                            c.status = "In Port"

                        db.add(MovementLog(
                            ship_id=ship.id,
                            origin_port_id=route.origin_port_id,
                            destination_port_id=dest_port.id,
                            details=f"Ship {ship.name} safely arrived and docked at port {dest_port.name}."
                        ))

                        await ws_manager.broadcast({
                            "type": "NOTIFICATION",
                            "level": "success",
                            "message": f"Ship '{ship.name}' arrived at Port '{dest_port.name}'."
                        })
                    else:
                        # Update position interpolating towards destination
                        ratio = speed / dist_remaining
                        ship.current_x = round(ship.current_x + dx * ratio, 2)
                        ship.current_y = round(ship.current_y + dy * ratio, 2)
                        total_dist = route.distance if route.distance > 0 else 1.0
                        route.progress = round(min(99.0, (1.0 - (dist_remaining / total_dist)) * 100.0), 1)

                db.commit()

                # Broadcast live state frame to WebSocket subscribers
                active_ships = db.query(Ship).all()
                ship_data = [{
                    "id": s.id,
                    "name": s.name,
                    "x": s.current_x,
                    "y": s.current_y,
                    "status": s.status,
                    "fuel": s.current_fuel,
                    "fuel_capacity": s.fuel_capacity,
                    "dest_id": s.destination_port_id,
                    "containers_count": len(s.containers)
                } for s in active_ships]

                await ws_manager.broadcast({
                    "type": "TICK",
                    "ticks": state.ticks_elapsed,
                    "status": state.status,
                    "ships": ship_data
                })

            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
                db.rollback()
            finally:
                db.close()

            await asyncio.sleep(1.0) # tick interval 1 second

simulation_engine = SimulationEngine()
