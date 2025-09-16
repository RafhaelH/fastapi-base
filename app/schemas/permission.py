"""Schemas para validação de dados de permissões."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """Schema base para permissão."""
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=200)
    resource: str = Field(max_length=50)
    action: str = Field(max_length=20)
    is_active: bool = True


class PermissionCreate(PermissionBase):
    """Schema para criação de permissão."""
    pass


class PermissionUpdate(BaseModel):
    """Schema para atualização de permissão."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=200)
    resource: Optional[str] = Field(None, max_length=50)
    action: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class PermissionOut(PermissionBase):
    """Schema de saída para permissão."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class RolePermissionAssign(BaseModel):
    """Schema para atribuir/remover permissões de um role."""
    permission_ids: list[int]


class UserRoleAssign(BaseModel):
    """Schema para atribuir/remover roles de um usuário."""
    role_ids: list[int]


class PermissionCheck(BaseModel):
    """Schema para verificação de permissão."""
    resource: str
    action: str


class PermissionList(BaseModel):
    """Schema para listagem paginada de permissões."""
    permissions: list[PermissionOut]
    total: int
    page: int
    per_page: int
    pages: int