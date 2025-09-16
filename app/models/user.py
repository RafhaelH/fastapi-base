"""Modelos para usuários e roles do sistema."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Table, Column, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    """Modelo para usuários do sistema.
    
    Representa um usuário com autenticação por email/senha e sistema de roles.
    Inclui campos para profile completo e auditoria.
    """
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Campos de perfil
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status e controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Reset de senha
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relacionamentos
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        back_populates="users", 
        secondary=user_roles, 
        lazy="selectin"
    )
    
    @property
    def full_name(self) -> str:
        """Retorna o nome completo do usuário."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email.split('@')[0]
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Verifica se o usuário possui uma permissão específica.
        
        Args:
            resource: Recurso da permissão (ex: 'users', 'admin')
            action: Ação da permissão (ex: 'read', 'write', 'delete')
            
        Returns:
            True se o usuário possui a permissão
        """
        if self.is_superuser:
            return True
            
        for role in self.roles:
            if not role.is_active:
                continue
            for permission in role.permissions:
                if (permission.is_active and 
                    permission.resource == resource and 
                    permission.action == action):
                    return True
        return False
    
    def has_role(self, role_name: str) -> bool:
        """Verifica se o usuário possui um role específico.
        
        Args:
            role_name: Nome do role
            
        Returns:
            True se o usuário possui o role
        """
        return any(role.name == role_name and role.is_active for role in self.roles)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"


class Role(Base):
    """Modelo para roles (grupos de permissões).
    
    Um role agrupa múltiplas permissões e pode ser atribuído a usuários.
    Exemplos: 'admin', 'user', 'moderator', 'editor'.
    """
    __tablename__ = "role"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(200), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Role padrão para novos usuários
    
    # Auditoria
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="roles", 
        secondary=user_roles
    )
    
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin"
    )
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Verifica se o role possui uma permissão específica.
        
        Args:
            resource: Recurso da permissão
            action: Ação da permissão
            
        Returns:
            True se o role possui a permissão
        """
        for permission in self.permissions:
            if (permission.is_active and 
                permission.resource == resource and 
                permission.action == action):
                return True
        return False
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}', active={self.is_active})>"
