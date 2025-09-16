"""Utilitários para segurança e criptografia."""
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings
from app.schemas.auth import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Gera hash da senha usando bcrypt.
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verifica se a senha confere com o hash.
    
    Args:
        plain_password: Senha em texto plano
        password_hash: Hash da senha
        
    Returns:
        True se a senha confere
    """
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(
    subject: str, 
    expires_minutes: Optional[int] = None,
    permissions: Optional[list[str]] = None
) -> str:
    """Cria um token de acesso JWT.
    
    Args:
        subject: Identificador do usuário (email)
        expires_minutes: Minutos para expiração (usa config se None)
        permissions: Lista de permissões do usuário
        
    Returns:
        Token JWT codificado
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "permissions": permissions or []
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Cria um refresh token JWT.
    
    Args:
        subject: Identificador do usuário (email)
        
    Returns:
        Refresh token JWT codificado
    """
    expire = datetime.now(timezone.utc) + timedelta(days=7)  # Refresh token válido por 7 dias
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> TokenPayload:
    """Verifica e decodifica um token JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        Payload do token decodificado
        
    Raises:
        HTTPException: Se o token for inválido
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # Verifica se o token não expirou
        exp = payload.get("exp")
        if not exp or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        
        # Verifica se tem subject
        subject = payload.get("sub")
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        return TokenPayload(
            sub=subject,
            exp=datetime.fromtimestamp(exp, tz=timezone.utc),
            iat=datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.utc),
            permissions=payload.get("permissions", [])
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


def generate_password_reset_token() -> str:
    """Gera um token seguro para reset de senha.
    
    Returns:
        Token de 32 caracteres
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))


def generate_verification_token() -> str:
    """Gera um token seguro para verificação de email.
    
    Returns:
        Token de 32 caracteres
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))
