"""Schemas para validação de dados de usuários."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Schema base para usuário com campos comuns."""
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(BaseModel):
    """Schema para criação de usuário."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    
    @validator('password')
    def validate_password(cls, v):
        """Valida se a senha atende aos critérios mínimos."""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('Senha deve ter pelo menos uma letra maiúscula')
        if not any(c.islower() for c in v):
            raise ValueError('Senha deve ter pelo menos uma letra minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('Senha deve ter pelo menos um número')
        return v


class UserUpdate(BaseModel):
    """Schema para atualização de usuário."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    """Schema para atualização de senha."""
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Valida se a nova senha atende aos critérios mínimos."""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('Senha deve ter pelo menos uma letra maiúscula')
        if not any(c.islower() for c in v):
            raise ValueError('Senha deve ter pelo menos uma letra minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('Senha deve ter pelo menos um número')
        return v


class RoleBase(BaseModel):
    """Schema base para role."""
    name: str = Field(max_length=50)
    description: str = Field(default="", max_length=200)
    is_active: bool = True
    is_default: bool = False


class RoleCreate(RoleBase):
    """Schema para criação de role."""
    pass


class RoleUpdate(BaseModel):
    """Schema para atualização de role."""
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class RoleOut(RoleBase):
    """Schema de saída para role."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class UserOut(UserBase):
    """Schema de saída para usuário."""
    id: int
    full_name: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    roles: list[RoleOut] = []

    model_config = {"from_attributes": True}


class UserWithRoles(UserOut):
    """Schema de usuário com informações completas de roles."""
    pass


class UserList(BaseModel):
    """Schema para listagem paginada de usuários."""
    users: list[UserOut]
    total: int
    page: int
    per_page: int
    pages: int
