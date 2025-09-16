"""Dependências para autenticação e autorização."""
from functools import wraps
from typing import Callable, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_token
from app.db.session import get_session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False
)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_session)
) -> Optional[User]:
    """Obtém o usuário atual a partir do token JWT.
    
    Args:
        token: Token JWT
        session: Sessão do banco de dados
        
    Returns:
        Usuário autenticado ou None se não autenticado
        
    Raises:
        HTTPException: Se o token for inválido
    """
    if not token:
        return None
        
    token_payload = verify_token(token)
    
    user = (await session.execute(
        select(User).where(User.email == token_payload.sub)
    )).scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo"
        )
    
    # Atualiza last_login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    await session.commit()
    
    return user


async def require_authenticated_user(
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """Requer que o usuário esteja autenticado.
    
    Args:
        user: Usuário atual
        
    Returns:
        Usuário autenticado
        
    Raises:
        HTTPException: Se não autenticado
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_verified_user(
    user: User = Depends(require_authenticated_user)
) -> User:
    """Requer que o usuário esteja verificado.
    
    Args:
        user: Usuário autenticado
        
    Returns:
        Usuário verificado
        
    Raises:
        HTTPException: Se não verificado
    """
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return user


async def require_superuser(
    user: User = Depends(require_authenticated_user)
) -> User:
    """Requer que o usuário seja superusuário.
    
    Args:
        user: Usuário autenticado
        
    Returns:
        Superusuário
        
    Raises:
        HTTPException: Se não for superusuário
    """
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required"
        )
    return user


def require_permission(resource: str, action: str):
    """Decorator para verificar permissões específicas.
    
    Args:
        resource: Recurso da permissão (ex: 'users', 'admin')
        action: Ação da permissão (ex: 'read', 'write', 'delete')
        
    Returns:
        Decorator function
    """
    def permission_checker(user: User = Depends(require_authenticated_user)) -> User:
        if not user.has_permission(resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {resource}:{action}"
            )
        return user
    
    return permission_checker


def require_role(role_name: str):
    """Decorator para verificar roles específicos.
    
    Args:
        role_name: Nome do role requerido
        
    Returns:
        Decorator function
    """
    def role_checker(user: User = Depends(require_authenticated_user)) -> User:
        if not user.has_role(role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role_name}"
            )
        return user
    
    return role_checker


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> Optional[User]:
    """Obtém o usuário atual se autenticado, senão retorna None.
    
    Esta função não gera exceções se o usuário não estiver autenticado.
    
    Args:
        token: Token JWT opcional
        session: Sessão do banco de dados
        
    Returns:
        Usuário autenticado ou None
    """
    if not token:
        return None
    
    try:
        token_payload = verify_token(token)
        user = (await session.execute(
            select(User).where(User.email == token_payload.sub)
        )).scalar_one_or_none()
        
        if user and user.is_active:
            return user
    except HTTPException:
        pass
    
    return None
