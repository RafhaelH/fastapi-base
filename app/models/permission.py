"""Modelos para sistema de permissões e grupos."""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Table, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True),
)


class Permission(Base):
    """Modelo para permissões do sistema.
    
    Uma permissão representa uma ação específica que pode ser realizada no sistema,
    como 'users:read', 'users:write', 'admin:access', etc.
    """
    __tablename__ = "permission"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(200), default="")
    resource: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # ex: 'users', 'admin', 'posts'
    action: Mapped[str] = mapped_column(String(20), nullable=False, index=True)    # ex: 'read', 'write', 'delete'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    roles: Mapped[list["Role"]] = relationship(
        "Role", 
        secondary=role_permissions, 
        back_populates="permissions",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Permission(name='{self.name}', resource='{self.resource}', action='{self.action}')>"
