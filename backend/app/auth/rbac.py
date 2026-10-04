from fastapi import Depends, HTTPException, status
from typing import List
from app.auth.security import get_current_user
from app.models.user import User

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role == "Administrator":
            return user  # Admin has permission for everything
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {self.allowed_roles}, your role: {user.role}"
            )
        return user

admin_only = RoleChecker(["Administrator"])
port_manager_or_admin = RoleChecker(["Administrator", "Port Manager"])
fleet_manager_or_admin = RoleChecker(["Administrator", "Fleet Manager"])
authenticated_user = RoleChecker(["Administrator", "Port Manager", "Fleet Manager", "Viewer"])
