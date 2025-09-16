"""Schemas para autenticação e autorização."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Schema para token de acesso."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # segundos
    refresh_token: Optional[str] = None


class LoginInput(BaseModel):
    """Schema para dados de login."""
    email: EmailStr
    password: str = Field(min_length=8)


class RefreshTokenInput(BaseModel):
    """Schema para refresh token."""
    refresh_token: str


class TokenPayload(BaseModel):
    """Schema para payload do token JWT."""
    sub: str  # subject (email do usuário)
    exp: datetime  # expiration
    iat: datetime  # issued at
    permissions: Optional[list[str]] = []  # lista de permissões


class PasswordReset(BaseModel):
    """Schema para solicitação de reset de senha."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema para confirmação de reset de senha."""
    token: str
    new_password: str = Field(min_length=8, max_length=100)
