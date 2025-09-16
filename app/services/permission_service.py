"""Serviços para gerenciamento de permissões."""
from math import ceil
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionList


class PermissionService:
    """Serviço para operações com permissões."""

    @staticmethod
    async def get_all_permissions(
        session: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> PermissionList:
        """Lista permissões com paginação e filtros.

        Args:
            session: Sessão do banco de dados
            page: Página atual (1-indexed)
            per_page: Itens por página
            search: Termo de busca (nome, descrição)
            resource: Filtro por recurso
            action: Filtro por ação
            is_active: Filtro por status ativo
            
        Returns:
            Lista paginada de permissões
        """
        query = select(Permission)

        # Aplicar filtros
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Permission.name.ilike(search_term),
                    Permission.description.ilike(search_term),
                    Permission.resource.ilike(search_term),
                    Permission.action.ilike(search_term)
                )
            )

        if resource:
            query = query.where(Permission.resource == resource)

        if action:
            query = query.where(Permission.action == action)

        if is_active is not None:
            query = query.where(Permission.is_active == is_active)

        # Contagem total
        count_query = select(func.count(Permission.id))
        if search:
            search_term = f"%{search}%"
            count_query = count_query.where(
                or_(
                    Permission.name.ilike(search_term),
                    Permission.description.ilike(search_term),
                    Permission.resource.ilike(search_term),
                    Permission.action.ilike(search_term)
                )
            )
        if resource:
            count_query = count_query.where(Permission.resource == resource)
        if action:
            count_query = count_query.where(Permission.action == action)
        if is_active is not None:
            count_query = count_query.where(Permission.is_active == is_active)

        total = (await session.execute(count_query)).scalar()

        # Paginação
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        # Ordenação
        query = query.order_by(Permission.resource, Permission.action, Permission.name)

        result = await session.execute(query)
        permissions = list(result.scalars().all())

        return PermissionList(
            permissions=permissions,
            total=total,
            page=page,
            per_page=per_page,
            pages=ceil(total / per_page) if total > 0 else 1
        )

    @staticmethod
    async def get_permission_by_id(permission_id: int, session: AsyncSession) -> Optional[Permission]:
        """Obtém permissão por ID.

        Args:
            permission_id: ID da permissão
            session: Sessão do banco de dados

        Returns:
            Permissão encontrada ou None
        """
        return (await session.execute(
            select(Permission).where(Permission.id == permission_id)
        )).scalar_one_or_none()

    @staticmethod
    async def get_permission_by_name(name: str, session: AsyncSession) -> Optional[Permission]:
        """Obtém permissão por nome.

        Args:
            name: Nome da permissão
            session: Sessão do banco de dados

        Returns:
            Permissão encontrada ou None
        """
        return (await session.execute(
            select(Permission).where(Permission.name == name)
        )).scalar_one_or_none()

    @staticmethod
    async def get_permission_by_resource_action(
        resource: str,
        action: str,
        session: AsyncSession
    ) -> Optional[Permission]:
        """Obtém permissão por recurso e ação.

        Args:
            resource: Recurso da permissão
            action: Ação da permissão
            session: Sessão do banco de dados

        Returns:
            Permissão encontrada ou None
        """
        return (await session.execute(
            select(Permission).where(
                Permission.resource == resource,
                Permission.action == action
            )
        )).scalar_one_or_none()

    @staticmethod
    async def create_permission(
        permission_data: PermissionCreate,
        session: AsyncSession
    ) -> Permission:
        """Cria uma nova permissão.

        Args:
            permission_data: Dados da permissão
            session: Sessão do banco de dados

        Returns:
            Permissão criada

        Raises:
            ValueError: Se nome ou combinação recurso/ação já existir
        """
        # Verifica se nome já existe
        exists_name = (await session.execute(
            select(Permission).where(Permission.name == permission_data.name)
        )).scalar_one_or_none()

        if exists_name:
            raise ValueError("Nome da permissão já existe")

        # Verifica se combinação resource/action já existe
        exists_combo = (await session.execute(
            select(Permission).where(
                Permission.resource == permission_data.resource,
                Permission.action == permission_data.action
            )
        )).scalar_one_or_none()

        if exists_combo:
            raise ValueError("Combinação recurso/ação já existe")

        # Cria a permissão
        new_permission = Permission(**permission_data.model_dump())
        session.add(new_permission)
        await session.commit()
        await session.refresh(new_permission)

        return new_permission

    @staticmethod
    async def update_permission(
        permission_id: int,
        permission_data: PermissionUpdate,
        session: AsyncSession
    ) -> Optional[Permission]:
        """Atualiza dados da permissão.

        Args:
            permission_id: ID da permissão
            permission_data: Dados para atualização
            session: Sessão do banco de dados

        Returns:
            Permissão atualizada ou None se não encontrada

        Raises:
            ValueError: Se novo nome ou combinação já existir
        """
        permission = (await session.execute(
            select(Permission).where(Permission.id == permission_id)
        )).scalar_one_or_none()

        if not permission:
            return None

        # Verifica se novo nome já existe (se fornecido)
        if permission_data.name and permission_data.name != permission.name:
            exists = (await session.execute(
                select(Permission).where(Permission.name == permission_data.name)
            )).scalar_one_or_none()

            if exists:
                raise ValueError("Nome da permissão já existe")

        # Verifica se nova combinação resource/action já existe
        if permission_data.resource or permission_data.action:
            new_resource = permission_data.resource or permission.resource
            new_action = permission_data.action or permission.action

            if new_resource != permission.resource or new_action != permission.action:
                exists = (await session.execute(
                    select(Permission).where(
                        Permission.resource == new_resource,
                        Permission.action == new_action,
                        Permission.id != permission_id
                    )
                )).scalar_one_or_none()

                if exists:
                    raise ValueError("Combinação recurso/ação já existe")

        # Atualiza apenas campos fornecidos
        update_data = permission_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(permission, field, value)

        await session.commit()
        await session.refresh(permission)

        return permission

    @staticmethod
    async def delete_permission(permission_id: int, session: AsyncSession) -> bool:
        """Remove permissão (soft delete).

        Args:
            permission_id: ID da permissão
            session: Sessão do banco de dados
            
        Returns:
            True se removido com sucesso
        """
        permission = (await session.execute(
            select(Permission).where(Permission.id == permission_id)
        )).scalar_one_or_none()

        if not permission:
            return False

        permission.is_active = False
        await session.commit()

        return True

    @staticmethod
    async def toggle_permission_status(
        permission_id: int,
        session: AsyncSession
    ) -> Optional[Permission]:
        """Alterna status ativo/inativo da permissão.

        Args:
            permission_id: ID da permissão
            session: Sessão do banco de dados
            
        Returns:
            Permissão atualizada ou None se não encontrada
        """
        permission = (await session.execute(
            select(Permission).where(Permission.id == permission_id)
        )).scalar_one_or_none()

        if not permission:
            return None

        permission.is_active = not permission.is_active
        await session.commit()
        await session.refresh(permission)

        return permission

    @staticmethod
    async def get_resources(session: AsyncSession) -> list[str]:
        """Obtém lista de recursos únicos.

        Args:
            session: Sessão do banco de dados

        Returns:
            Lista de recursos únicos
        """
        result = await session.execute(
            select(Permission.resource).distinct().order_by(Permission.resource)
        )
        return [row[0] for row in result.fetchall()]

    @staticmethod
    async def get_actions(session: AsyncSession) -> list[str]:
        """Obtém lista de ações únicas.

        Args:
            session: Sessão do banco de dados
            
        Returns:
            Lista de ações únicas
        """
        result = await session.execute(
            select(Permission.action).distinct().order_by(Permission.action)
        )
        return [row[0] for row in result.fetchall()]

    @staticmethod
    async def create_default_permissions(session: AsyncSession) -> None:
        """Cria permissões padrão do sistema.

        Args:
            session: Sessão do banco de dados
        """
        default_permissions = [
            # Usuários
            {"name": "users:read", "description": "Visualizar usuários", "resource": "users", "action": "read"},
            {"name": "users:write", "description": "Criar e editar usuários", "resource": "users", "action": "write"},
            {"name": "users:delete", "description": "Excluir usuários", "resource": "users", "action": "delete"},

            # Roles
            {"name": "roles:read", "description": "Visualizar roles", "resource": "roles", "action": "read"},
            {"name": "roles:write", "description": "Criar e editar roles", "resource": "roles", "action": "write"},
            {"name": "roles:delete", "description": "Excluir roles", "resource": "roles", "action": "delete"},

            # Permissões
            {"name": "permissions:read", "description": "Visualizar permissões", "resource": "permissions", "action": "read"},
            {"name": "permissions:write", "description": "Criar e editar permissões", "resource": "permissions", "action": "write"},
            {"name": "permissions:delete", "description": "Excluir permissões", "resource": "permissions", "action": "delete"},

            # Admin
            {"name": "admin:access", "description": "Acesso ao painel administrativo", "resource": "admin", "action": "access"},
            {"name": "admin:settings", "description": "Gerenciar configurações do sistema", "resource": "admin", "action": "settings"},
        ]

        for perm_data in default_permissions:
            exists = (await session.execute(
                select(Permission).where(
                    Permission.resource == perm_data["resource"],
                    Permission.action == perm_data["action"]
                )
            )).scalar_one_or_none()

            if not exists:
                permission = Permission(**perm_data)
                session.add(permission)

        await session.commit()
