"""Configurações da aplicação."""
import os
from typing import List, Optional

from pydantic import validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação usando Pydantic BaseSettings."""
    
    # Aplicação
    PROJECT_NAME: str = "FastAPI Base"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Segurança
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_ALGORITHM: str = "HS256"
    
    # Banco de Dados
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_base"
    SYNC_DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_base"
    
    # CORS
    CORS_ORIGINS: str = Field(default="", json_schema_extra={"format": "text"})
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Email (para funcionalidades futuras)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    
    # Upload de arquivos
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v) -> str:
        """Converte string separada por vírgulas em string."""
        if v is None:
            return ""
        return str(v)

    @property
    def cors_origins_list(self) -> List[str]:
        """Retorna CORS_ORIGINS como lista."""
        if not self.CORS_ORIGINS:
            return []
        return [i.strip() for i in self.CORS_ORIGINS.split(",") if i.strip()]
    
    @validator("CELERY_BROKER_URL", pre=True, always=True)
    def set_celery_broker_url(cls, v: Optional[str], values: dict) -> str:
        """Define CELERY_BROKER_URL baseado no REDIS_URL se não fornecido."""
        if v:
            return v
        return values.get("REDIS_URL", "redis://localhost:6379/0")
    
    @validator("CELERY_RESULT_BACKEND", pre=True, always=True)
    def set_celery_result_backend(cls, v: Optional[str], values: dict) -> str:
        """Define CELERY_RESULT_BACKEND baseado no REDIS_URL se não fornecido."""
        if v:
            return v
        return values.get("REDIS_URL", "redis://localhost:6379/0")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
