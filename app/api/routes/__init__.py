"""Módulo de rotas da API."""
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.me import router as me_router
from app.api.routes.permissions import router as permissions_router
from app.api.routes.roles import router as roles_router
from app.api.routes.users import router as users_router

__all__ = [
    "auth_router",
    "health_router", 
    "me_router",
    "permissions_router",
    "roles_router",
    "users_router"
]