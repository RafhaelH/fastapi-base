"""Rotas para gerenciamento de usuários."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission, require_authenticated_user
from app.db.session import get_session
from app.schemas.user import UserOut, UserUpdate, UserList
from app.schemas.permission import UserRoleAssign
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Usuários"])


@router.get("/", response_model=UserList, summary="Listar usuários")
async def list_users(
    page: int = Query(1, ge=1, description="Página"),
    per_page: int = Query(20, ge=1, le=100, description="Itens por página"),
    search: Optional[str] = Query(None, description="Buscar por email ou nome"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("users", "read"))
):
    """Lista usuários com paginação e filtros."""
    return await UserService.get_all_users(
        session=session,
        page=page,
        per_page=per_page,
        search=search,
        is_active=is_active
    )


@router.get("/{user_id}", response_model=UserOut, summary="Obter usuário por ID")
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("users", "read"))
):
    """Obtém um usuário específico por ID."""
    user = await UserService.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user


@router.put("/{user_id}", response_model=UserOut, summary="Atualizar usuário")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_authenticated_user)
):
    """Atualiza dados de um usuário.
    
    Usuários podem atualizar seus próprios dados ou usuários com permissão
    podem atualizar qualquer usuário.
    """
    # Verifica se é o próprio usuário ou tem permissão
    if current_user.id != user_id:
        if not current_user.has_permission("users", "write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para atualizar este usuário"
            )
    
    user = await UserService.update_user(user_id, user_data, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user


@router.delete("/{user_id}", summary="Desativar usuário")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("users", "delete"))
):
    """Desativa um usuário (soft delete)."""
    success = await UserService.delete_user(user_id, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return {"message": "Usuário desativado com sucesso"}


@router.post("/{user_id}/toggle-status", response_model=UserOut, summary="Alternar status do usuário")
async def toggle_user_status(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("users", "write"))
):
    """Alterna o status ativo/inativo de um usuário."""
    user = await UserService.toggle_user_status(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user


@router.post("/{user_id}/roles", summary="Atribuir roles ao usuário")
async def assign_roles_to_user(
    user_id: int,
    role_data: UserRoleAssign,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("users", "write"))
):
    """Atribui roles a um usuário."""
    user = await UserService.get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Remove todos os roles atuais e adiciona os novos
    user.roles = []
    await session.commit()
    
    for role_id in role_data.role_ids:
        success = await UserService.assign_role_to_user(user_id, role_id, session)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao atribuir role {role_id}"
            )
    
    return {"message": "Roles atribuídos com sucesso"}


@router.delete("/{user_id}/roles/{role_id}", summary="Remover role do usuário")
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("users", "write"))
):
    """Remove um role específico de um usuário."""
    success = await UserService.remove_role_from_user(user_id, role_id, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return {"message": "Role removido com sucesso"}
