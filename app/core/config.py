"""Configurações da aplicação."""
from typing import List, Optional

from pydantic import validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação usando Pydantic BaseSettings."""
    
    # Aplicação
    PROJECT_NAME: str = "FastAPI Base"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    ENV: str = "production"
    LOG_LEVEL: str = "INFO"

    # Segurança
    SECRET_KEY: str
    JWT_SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"
    
    # Banco de Dados
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    
    # CORS
    CORS_ORIGINS: str = Field(default="", json_schema_extra={"format": "text"})
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Email - SMTP
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    EMAIL_FROM_NAME: str = "FastAPI Base"

    # URLs para frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
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

    @validator("JWT_SECRET_KEY", pre=True, always=True)
    def set_jwt_secret_key(cls, v: Optional[str], values: dict) -> str:
        """Define JWT_SECRET_KEY baseado no SECRET_KEY se não fornecido."""
        if v:
            return v
        return values.get("SECRET_KEY", "")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
