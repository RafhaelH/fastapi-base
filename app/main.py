"""Aplicação principal FastAPI com sistema de autenticação e RBAC."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.api.routes import (
    auth_router,
    me_router,
    users_router,
    roles_router,
    permissions_router,
    health_router
)

# Criação da aplicação
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sistema base FastAPI com autenticação JWT e RBAC completo",
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Middleware de segurança
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or (["*"] if settings.DEBUG else []),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Rotas da API
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(me_router, prefix=settings.API_V1_PREFIX)
app.include_router(users_router, prefix=settings.API_V1_PREFIX)
app.include_router(roles_router, prefix=settings.API_V1_PREFIX)
app.include_router(permissions_router, prefix=settings.API_V1_PREFIX)
app.include_router(health_router)


@app.get("/", tags=["Sistema"])
async def root():
    """Endpoint raiz com informações básicas da API."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "online",
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "redoc": f"{settings.API_V1_PREFIX}/redoc"
    }


@app.get("/info", tags=["Sistema"])
async def info():
    """Informações detalhadas do sistema."""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": settings.ENV,
        "debug": settings.DEBUG,
        "features": [
            "JWT Authentication",
            "Role-Based Access Control (RBAC)",
            "User Management",
            "Permission Management",
            "RESTful API",
            "Auto-generated Documentation",
            "Docker Support"
        ]
    }
