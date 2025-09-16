"""Rotas para autenticação."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_authenticated_user
from app.db.session import get_session
from app.schemas.auth import (
    LoginInput, 
    Token, 
    RefreshTokenInput,
    PasswordReset,
    PasswordResetConfirm
)
from app.schemas.user import UserCreate, UserOut, UserPasswordUpdate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token, summary="Autenticação por email/senha")
async def login(
    data: LoginInput, 
    session: AsyncSession = Depends(get_session)
):
    """Autentica um usuário com email e senha.
    
    Retorna um token de acesso JWT e um refresh token para renovação.
    """
    token = await AuthService.authenticate(data.email, data.password, session)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciais inválidas"
        )
    return token


@router.post("/token", response_model=Token, summary="Autenticação OAuth2 (compatibilidade)")
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    """Endpoint de autenticação compatível com OAuth2.
    
    Este endpoint é usado pelo FastAPI para autenticação automática na documentação.
    """
    token = await AuthService.authenticate(form_data.username, form_data.password, session)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@router.post("/refresh", response_model=Token, summary="Renovar token de acesso")
async def refresh_token(
    data: RefreshTokenInput,
    session: AsyncSession = Depends(get_session)
):
    """Renova um token de acesso usando o refresh token."""
    token = await AuthService.refresh_token(data.refresh_token, session)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )
    return token


@router.post("/register", response_model=UserOut, summary="Registrar novo usuário")
async def register(
    payload: UserCreate, 
    session: AsyncSession = Depends(get_session)
):
    """Registra um novo usuário no sistema.
    
    O usuário será criado com o role padrão se existir.
    """
    try:
        user = await AuthService.register(
            email=payload.email,
            password=payload.password,
            session=session,
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone=payload.phone
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/change-password", summary="Alterar senha")
async def change_password(
    data: UserPasswordUpdate,
    current_user = Depends(require_authenticated_user),
    session: AsyncSession = Depends(get_session)
):
    """Altera a senha do usuário autenticado."""
    success = await AuthService.change_password(
        user=current_user,
        current_password=data.current_password,
        new_password=data.new_password,
        session=session
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    return {"message": "Senha alterada com sucesso"}


@router.post("/logout", summary="Fazer logout")
async def logout(
    current_user = Depends(require_authenticated_user)
):
    """Faz logout do usuário.
    
    Nota: Como usamos JWT stateless, o logout é feito no lado cliente
    removendo o token. Em implementações futuras, pode-se adicionar
    uma blacklist de tokens.
    """
    return {"message": "Logout realizado com sucesso"}


@router.get("/me/permissions", summary="Obter permissões do usuário")
async def get_my_permissions(
    current_user = Depends(require_authenticated_user)
):
    """Retorna todas as permissões do usuário autenticado."""
    permissions = await AuthService.get_user_permissions(current_user)
    return {"permissions": permissions}
