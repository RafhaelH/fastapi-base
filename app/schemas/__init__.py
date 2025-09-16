"""Schemas Pydantic para validação de dados."""
from app.schemas.auth import Token, LoginInput, RefreshTokenInput, TokenPayload
from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserOut, UserPasswordUpdate,
    RoleBase, RoleCreate, RoleUpdate, RoleOut, UserList
)
from app.schemas.permission import (
    PermissionBase, PermissionCreate, PermissionUpdate, PermissionOut,
    PermissionList, RolePermissionAssign, UserRoleAssign, PermissionCheck
)

__all__ = [
    # Auth
    "Token", "LoginInput", "RefreshTokenInput", "TokenPayload",
    # User
    "UserBase", "UserCreate", "UserUpdate", "UserOut", "UserPasswordUpdate",
    "RoleBase", "RoleCreate", "RoleUpdate", "RoleOut", "UserList",
    # Permission
    "PermissionBase", "PermissionCreate", "PermissionUpdate", "PermissionOut",
    "PermissionList", "RolePermissionAssign", "UserRoleAssign", "PermissionCheck"
]
