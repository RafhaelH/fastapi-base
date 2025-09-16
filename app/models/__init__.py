"""Modelos SQLAlchemy da aplicacao."""
from app.models.user import User, Role
from app.models.permission import Permission

__all__ = ["User", "Role", "Permission"]
