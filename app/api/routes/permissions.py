"""Rotas para gerenciamento de permissões."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.db.session import get_session
from app.schemas.permission import (
    PermissionOut, 
    PermissionCreate, 
    PermissionUpdate, 
    PermissionList
)
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/permissions", tags=["Permissões"])


@router.get("/", response_model=PermissionList, summary="Listar permissões")
async def list_permissions(
    page: int = Query(1, ge=1, description="Página"),
    per_page: int = Query(20, ge=1, le=100, description="Itens por página"),
    search: Optional[str] = Query(None, description="Buscar por nome, descrição, recurso ou ação"),
    resource: Optional[str] = Query(None, description="Filtrar por recurso"),
    action: Optional[str] = Query(None, description="Filtrar por ação"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("permissions", "read"))
):
    """Lista permissões com paginação e filtros."""
    return await PermissionService.get_all_permissions(
        session=session,
        page=page,
        per_page=per_page,
        search=search,
        resource=resource,
        action=action,
        is_active=is_active
    )


@router.get("/resources", summary="Listar recursos únicos")
async def list_resources(
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("permissions", "read"))
):
    """Lista todos os recursos únicos do sistema."""
    resources = await PermissionService.get_resources(session)
    return {"resources": resources}


@router.get("/actions", summary="Listar ações únicas")
async def list_actions(
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("permissions", "read"))
):
    """Lista todas as ações únicas do sistema."""
    actions = await PermissionService.get_actions(session)
    return {"actions": actions}


@router.get("/{permission_id}", response_model=PermissionOut, summary="Obter permissão por ID")
async def get_permission(
    permission_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("permissions", "read"))
):
    """Obtém uma permissão específica por ID."""
    permission = await PermissionService.get_permission_by_id(permission_id, session)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permissão não encontrada"
        )
    return permission


@router.post("/", response_model=PermissionOut, summary="Criar permissão")
async def create_permission(
    permission_data: PermissionCreate,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("permissions", "write"))
):
    """Cria uma nova permissão."""
    try:
        permission = await PermissionService.create_permission(permission_data, session)
        return permission
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{permission_id}", response_model=PermissionOut, summary="Atualizar permissão")
async def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("permissions", "write"))
):
    """Atualiza dados de uma permissão."""
    try:
        permission = await PermissionService.update_permission(
            permission_id, 
            permission_data, 
            session
        )
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permissão não encontrada"
            )
        return permission
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{permission_id}", summary="Desativar permissão")
async def delete_permission(
    permission_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("permissions", "delete"))
):
    """Desativa uma permissão (soft delete)."""
    success = await PermissionService.delete_permission(permission_id, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permissão não encontrada"
        )
    return {"message": "Permissão desativada com sucesso"}


@router.post("/{permission_id}/toggle-status", response_model=PermissionOut, summary="Alternar status da permissão")
async def toggle_permission_status(
    permission_id: int,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("permissions", "write"))
):
    """Alterna o status ativo/inativo de uma permissão."""
    permission = await PermissionService.toggle_permission_status(permission_id, session)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permissão não encontrada"
        )
    return permission


@router.post("/create-defaults", summary="Criar permissões padrão")
async def create_default_permissions(
    session: AsyncSession = Depends(get_session),
    _: None = Depends(require_permission("permissions", "write"))
):
    """Cria as permissões padrão do sistema."""
    await PermissionService.create_default_permissions(session)
    return {"message": "Permissões padrão criadas com sucesso"}