import os

class Settings:
    PROJECT_NAME: str = "PortFlow - Maritime Logistics & Port Simulation"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-portflow-jwt-key-2026-change-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./portflow.db")

settings = Settings()
