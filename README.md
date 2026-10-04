# PortFlow - Maritime Logistics & Port Management Simulation

PortFlow is an enterprise-grade full-stack web application designed for maritime logistics management and real-time port simulation. Built using **FastAPI, SQLAlchemy, SQLite/PostgreSQL, WebSockets, HTML5, Bootstrap 5, Chart.js, and Leaflet.js**.

---

## 🌟 Key Features

1. **Role-Based Access Control (RBAC)**:
   - **Administrator**: Full system access, user management, and simulation controls.
   - **Port Manager**: Manage port capacities, container inventory, loading/unloading operations.
   - **Fleet Manager**: Manage ships, route dispatch, refueling, and maintenance.
   - **Viewer**: Read-only dashboard and telemetry observation.

2. **SRS Business Validation Engine**:
   - Ship maximum cargo weight enforcement.
   - Heavy container limit verification.
   - Refrigerated container limit verification.
   - Liquid container limit verification.
   - Cartesian distance navigation formula \( \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2} \).
   - Dynamic fuel consumption calculation taking into account distance, cargo weight, and specific container type power factors.

3. **Real-time Simulation Workbench**:
   - Interactive 2D Cartesian navigation grid canvas.
   - Live WebSocket state broadcasting (`TICK`, `EVENT`, `NOTIFICATION`).
   - Controls for Start, Pause, Resume, Stop, Reset, and Speed Multipliers.

4. **Analytics & Data Reports**:
   - Executive dashboard cards and interactive Chart.js visualizations.
   - Audit logs for ship movement history and fuel transactions.
   - Export CSV spreadsheets for Ports, Ships, and Containers.

---

## 🛠️ Quick Start Guide

### Prerequisites
- Python 3.10+
- `pip` package manager

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python main.py
```
Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser at **`http://localhost:8000`**.

---

## 🔐 Default Demo Accounts

| Username | Password | Role |
| :--- | :--- | :--- |
| `admin` | `admin123` | Administrator |
| `portmgr` | `port123` | Port Manager |
| `fleetmgr` | `fleet123` | Fleet Manager |
| `viewer` | `viewer123` | Viewer |

---

## 🧪 Running Unit Tests
```bash
pytest backend/tests
```

---

## 🐳 Docker Deployment
```bash
docker-compose up --build
```
