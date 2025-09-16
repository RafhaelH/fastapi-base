"""Rotas para informações do usuário atual."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_authenticated_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/me", tags=["Perfil"])


@router.get("/", response_model=UserOut, summary="Obter dados do usuário autenticado")
async def get_current_user_profile(
    current_user: User = Depends(require_authenticated_user)
) -> UserOut:
    """Retorna os dados do usuário autenticado."""
    return current_user


@router.put("/", response_model=UserOut, summary="Atualizar perfil do usuário")
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(require_authenticated_user),
    session: AsyncSession = Depends(get_session)
) -> UserOut:
    """Atualiza o perfil do usuário autenticado."""
    updated_user = await UserService.update_user(
        user_id=current_user.id,
        user_data=user_data,
        session=session
    )
    return updated_user
