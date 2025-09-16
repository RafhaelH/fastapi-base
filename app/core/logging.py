"""Configuração do sistema de logging."""
import sys
from pathlib import Path
from loguru import logger

from app.core.config import settings


def setup_logging():
    """Configura o sistema de logging da aplicação."""
    # Remove handler padrão
    logger.remove()
    
    # Formato personalizado
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Console output
    logger.add(
        sys.stdout,
        format=log_format,
        level=getattr(settings, "LOG_LEVEL", "INFO"),
        colorize=True,
    )
    
    # File output apenas em produção
    if not settings.DEBUG:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Log geral
        logger.add(
            log_dir / "app.log",
            format=log_format,
            level="INFO",
            rotation="1 day",
            retention="30 days",
            compression="zip",
        )
        
        # Log de erros
        logger.add(
            log_dir / "errors.log",
            format=log_format,
            level="ERROR",
            rotation="1 day",
            retention="30 days",
            compression="zip",
        )


# Configurar logging na importação
setup_logging()
