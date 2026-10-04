import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal, engine, Base
from app.models import User, Port, Ship, Container, SimulationState
from app.auth.security import get_password_hash

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Create Default Users if not exist
        if db.query(User).count() == 0:
            users = [
                User(username="admin", email="admin@portflow.com", full_name="System Administrator", hashed_password=get_password_hash("admin123"), role="Administrator"),
                User(username="portmgr", email="portmgr@portflow.com", full_name="Chief Port Manager", hashed_password=get_password_hash("port123"), role="Port Manager"),
                User(username="fleetmgr", email="fleetmgr@portflow.com", full_name="Fleet Director", hashed_password=get_password_hash("fleet123"), role="Fleet Manager"),
                User(username="viewer", email="viewer@portflow.com", full_name="Logistics Analyst", hashed_password=get_password_hash("viewer123"), role="Viewer"),
            ]
            db.add_all(users)
            db.commit()
            print("Users seeded successfully.")

        # 2. Create Default Ports
        if db.query(Port).count() == 0:
            ports = [
                Port(name="Port of Rotterdam", x_coord=10.0, y_coord=15.0, dock_capacity=6, available_storage=200),
                Port(name="Port of Singapore", x_coord=85.0, y_coord=70.0, dock_capacity=10, available_storage=500),
                Port(name="Port of Shanghai", x_coord=120.0, y_coord=80.0, dock_capacity=8, available_storage=450),
                Port(name="Port of Los Angeles", x_coord=20.0, y_coord=90.0, dock_capacity=5, available_storage=300),
                Port(name="Port of Hamburg", x_coord=15.0, y_coord=25.0, dock_capacity=4, available_storage=180),
            ]
            db.add_all(ports)
            db.commit()
            print("Ports seeded successfully.")

        # Get port IDs
        rotterdam = db.query(Port).filter(Port.name == "Port of Rotterdam").first()
        singapore = db.query(Port).filter(Port.name == "Port of Singapore").first()
        shanghai = db.query(Port).filter(Port.name == "Port of Shanghai").first()

        # 3. Create Default Ships
        if db.query(Ship).count() == 0:
            ships = [
                Ship(name="Ever Given", max_weight=5000.0, fuel_capacity=1200.0, current_fuel=1000.0, heavy_limit=20, refrigerated_limit=15, liquid_limit=10, current_port_id=rotterdam.id, current_x=rotterdam.x_coord, current_y=rotterdam.y_coord, status="Docked"),
                Ship(name="Maersk Mc-Kinney", max_weight=6000.0, fuel_capacity=1500.0, current_fuel=1400.0, heavy_limit=25, refrigerated_limit=20, liquid_limit=15, current_port_id=singapore.id, current_x=singapore.x_coord, current_y=singapore.y_coord, status="Docked"),
                Ship(name="CMA CGM Antoine", max_weight=4500.0, fuel_capacity=1000.0, current_fuel=850.0, heavy_limit=15, refrigerated_limit=15, liquid_limit=10, current_port_id=shanghai.id, current_x=shanghai.x_coord, current_y=shanghai.y_coord, status="Docked"),
                Ship(name="HMM Algeciras", max_weight=7000.0, fuel_capacity=2000.0, current_fuel=1900.0, heavy_limit=30, refrigerated_limit=25, liquid_limit=20, current_port_id=rotterdam.id, current_x=rotterdam.x_coord, current_y=rotterdam.y_coord, status="Docked")
            ]
            db.add_all(ships)
            db.commit()
            print("Ships seeded successfully.")

        ship1 = db.query(Ship).filter(Ship.name == "Ever Given").first()

        # 4. Create Default Containers
        if db.query(Container).count() == 0:
            containers = [
                Container(container_code="CONT-1001", type="Basic", weight=25.0, current_port_id=rotterdam.id, status="In Port"),
                Container(container_code="CONT-1002", type="Heavy", weight=45.0, current_port_id=rotterdam.id, status="In Port"),
                Container(container_code="CONT-1003", type="Refrigerated", weight=30.0, assigned_ship_id=ship1.id, status="On Ship"),
                Container(container_code="CONT-1004", type="Liquid", weight=35.0, assigned_ship_id=ship1.id, status="On Ship"),
                Container(container_code="CONT-1005", type="Basic", weight=20.0, current_port_id=singapore.id, status="In Port"),
                Container(container_code="CONT-1006", type="Heavy", weight=50.0, current_port_id=shanghai.id, status="In Port"),
            ]
            db.add_all(containers)
            db.commit()
            print("Containers seeded successfully.")

        # 5. Initialize Simulation State
        if db.query(SimulationState).count() == 0:
            state = SimulationState(status="Stopped", speed_multiplier=1.0, ticks_elapsed=0)
            db.add(state)
            db.commit()

        print("PortFlow Seeding Completed Successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
