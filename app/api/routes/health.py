"""Rotas para verificação de saúde do sistema."""
import asyncio
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session

router = APIRouter(tags=["Sistema"])


@router.get("/health", summary="Verificação básica de saúde")
async def health_check() -> Dict[str, Any]:
    """Verificação básica de saúde da aplicação."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENV
    }


@router.get("/health/detailed", summary="Verificação detalhada de saúde")
async def detailed_health_check(
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Verificação detalhada de saúde incluindo dependências."""
    checks = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENV,
        "checks": {}
    }
    
    # Verificação do banco de dados
    try:
        start_time = asyncio.get_event_loop().time()
        await session.execute(text("SELECT 1"))
        db_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        checks["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": round(db_time, 2)
        }
    except Exception as e:
        checks["status"] = "unhealthy"
        checks["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Verificação do Redis (se configurado)
    try:
        import redis
        redis_client = redis.from_url(settings.REDIS_URL)
        start_time = asyncio.get_event_loop().time()
        redis_client.ping()
        redis_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        checks["checks"]["redis"] = {
            "status": "healthy",
            "response_time_ms": round(redis_time, 2)
        }
    except Exception as e:
        checks["status"] = "unhealthy"
        checks["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Se algum check falhou, retorna 503
    if checks["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=checks
        )
    
    return checks


@router.get("/health/readiness", summary="Verificação de prontidão")
async def readiness_check(
    session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    """Verificação se a aplicação está pronta para receber tráfego."""
    try:
        # Verifica se consegue fazer query no banco
        await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not ready", "reason": "database not available"}
        )


@router.get("/health/liveness", summary="Verificação de vida")
async def liveness_check() -> Dict[str, str]:
    """Verificação se a aplicação está viva."""
    return {"status": "alive"}
