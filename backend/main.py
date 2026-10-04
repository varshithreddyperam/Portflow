import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database.session import engine, Base
from app.routers import (
    auth_router,
    user_router,
    port_router,
    ship_router,
    container_router,
    route_router,
    simulation_router,
    report_router
)
from seed import seed_database

# Create DB tables automatically
Base.metadata.create_all(bind=engine)

# Run initial seed check
try:
    seed_database()
except Exception as e:
    print(f"Seed initialization note: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Port Management & Maritime Logistics Simulation REST APIs",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(port_router.router)
app.include_router(ship_router.router)
app.include_router(container_router.router)
app.include_router(route_router.router)
app.include_router(simulation_router.router)
app.include_router(report_router.router)

# Mount Frontend Static Files & Folders
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    js_dir = os.path.join(frontend_dir, "js")
    css_dir = os.path.join(frontend_dir, "css")
    
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))

    @app.get("/{page_name}.html")
    def serve_html_pages(page_name: str):
        page_path = os.path.join(frontend_dir, f"{page_name}.html")
        if os.path.exists(page_path):
            return FileResponse(page_path)
        return FileResponse(os.path.join(frontend_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
