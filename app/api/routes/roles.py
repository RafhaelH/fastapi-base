"""Rotas para gerenciamento de roles."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.db.session import get_session
from app.schemas.user import RoleOut, RoleCreate, RoleUpdate
from app.schemas.permission import RolePermissionAssign
from app.services.role_service import RoleService

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", summary="Listar roles")
async def list_roles(
    page: int = Query(1, ge=1, description="Página"),
    per_page: int = Query(20, ge=1, le=100, description="Itens por página"),
    search: Optional[str] = Query(None, description="Buscar por nome ou descrição"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("roles", "read"))
):
    """Lista roles com paginação e filtros."""
    return await RoleService.get_all_roles(
        session=session,
        page=page,
        per_page=per_page,
        search=search,
        is_active=is_active
    )


@router.get("/{role_id}", response_model=RoleOut, summary="Obter role por ID")
async def get_role(
    role_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("roles", "read"))
):
    """Obtém um role específico por ID."""
    role = await RoleService.get_role_by_id(role_id, session)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado"
        )
    return role


@router.post("/", response_model=RoleOut, summary="Criar role")
async def create_role(
    role_data: RoleCreate,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("roles", "write"))
):
    """Cria um novo role."""
    try:
        role = await RoleService.create_role(role_data, session)
        return role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{role_id}", response_model=RoleOut, summary="Atualizar role")
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("roles", "write"))
):
    """Atualiza dados de um role."""
    try:
        role = await RoleService.update_role(role_id, role_data, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role não encontrado"
            )
        return role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{role_id}", summary="Desativar role")
async def delete_role(
    role_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("roles", "delete"))
):
    """Desativa um role (soft delete)."""
    success = await RoleService.delete_role(role_id, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado"
        )
    return {"message": "Role desativado com sucesso"}


@router.post("/{role_id}/toggle-status", response_model=RoleOut, summary="Alternar status do role")
async def toggle_role_status(
    role_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("roles", "write"))
):
    """Alterna o status ativo/inativo de um role."""
    role = await RoleService.toggle_role_status(role_id, session)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado"
        )
    return role


@router.post("/{role_id}/permissions", summary="Definir permissões do role")
async def set_role_permissions(
    role_id: int,
    permission_data: RolePermissionAssign,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("roles", "write"))
):
    """Define as permissões de um role (substitui todas as existentes)."""
    success = await RoleService.set_role_permissions(
        role_id, 
        permission_data.permission_ids, 
        session
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado"
        )
    
    return {"message": "Permissões definidas com sucesso"}


@router.post("/{role_id}/permissions/{permission_id}", summary="Adicionar permissão ao role")
async def add_permission_to_role(
    role_id: int,
    permission_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("roles", "write"))
):
    """Adiciona uma permissão específica a um role."""
    success = await RoleService.assign_permission_to_role(role_id, permission_id, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role ou permissão não encontrado"
        )
    
    return {"message": "Permissão adicionada com sucesso"}


@router.delete("/{role_id}/permissions/{permission_id}", summary="Remover permissão do role")
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("roles", "write"))
):
    """Remove uma permissão específica de um role."""
    success = await RoleService.remove_permission_from_role(role_id, permission_id, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado"
        )
    
    return {"message": "Permissão removida com sucesso"}


@router.post("/{role_id}/set-default", summary="Definir como role padrão")
async def set_default_role(
    role_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("roles", "write"))
):
    """Define um role como padrão para novos usuários."""
    success = await RoleService.set_default_role(role_id, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrado"
        )
    
    return {"message": "Role definido como padrão"}
