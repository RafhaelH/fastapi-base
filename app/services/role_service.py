"""Serviços para gerenciamento de roles."""
from math import ceil
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.models.user import Role
from app.models.permission import Permission
from app.schemas.user import RoleCreate, RoleUpdate
from app.schemas.permission import PermissionList


class RoleService:
    """Serviço para operações com roles."""
    
    @staticmethod
    async def get_all_roles(
        session: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> dict:
        """Lista roles com paginação e filtros.
        
        Args:
            session: Sessão do banco de dados
            page: Página atual (1-indexed)
            per_page: Itens por página
            search: Termo de busca (nome, descrição)
            is_active: Filtro por status ativo
            
        Returns:
            Lista paginada de roles
        """
        query = select(Role).options(selectinload(Role.permissions))
        
        # Aplicar filtros
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Role.name.ilike(search_term),
                    Role.description.ilike(search_term)
                )
            )
        
        if is_active is not None:
            query = query.where(Role.is_active == is_active)
        
        # Contagem total
        count_query = select(func.count(Role.id))
        if search:
            search_term = f"%{search}%"
            count_query = count_query.where(
                or_(
                    Role.name.ilike(search_term),
                    Role.description.ilike(search_term)
                )
            )
        if is_active is not None:
            count_query = count_query.where(Role.is_active == is_active)
        
        total = (await session.execute(count_query)).scalar()
        
        # Paginação
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        # Ordenação
        query = query.order_by(Role.created_at.desc())
        
        result = await session.execute(query)
        roles = list(result.scalars().all())
        
        return {
            "roles": roles,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": ceil(total / per_page) if total > 0 else 1
        }

    @staticmethod
    async def get_role_by_id(role_id: int, session: AsyncSession) -> Optional[Role]:
        """Obtém role por ID.
        
        Args:
            role_id: ID do role
            session: Sessão do banco de dados
            
        Returns:
            Role encontrado ou None
        """
        return (await session.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )).scalar_one_or_none()

    @staticmethod
    async def get_role_by_name(name: str, session: AsyncSession) -> Optional[Role]:
        """Obtém role por nome.
        
        Args:
            name: Nome do role
            session: Sessão do banco de dados
            
        Returns:
            Role encontrado ou None
        """
        return (await session.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.name == name)
        )).scalar_one_or_none()

    @staticmethod
    async def create_role(role_data: RoleCreate, session: AsyncSession) -> Role:
        """Cria um novo role.
        
        Args:
            role_data: Dados do role
            session: Sessão do banco de dados
            
        Returns:
            Role criado
            
        Raises:
            ValueError: Se nome já existir
        """
        # Verifica se nome já existe
        exists = (await session.execute(
            select(Role).where(Role.name == role_data.name)
        )).scalar_one_or_none()
        
        if exists:
            raise ValueError("Nome do role já existe")
        
        # Cria o role
        new_role = Role(**role_data.model_dump())
        session.add(new_role)
        await session.commit()
        await session.refresh(new_role)
        
        return new_role

    @staticmethod
    async def update_role(
        role_id: int,
        role_data: RoleUpdate,
        session: AsyncSession
    ) -> Optional[Role]:
        """Atualiza dados do role.
        
        Args:
            role_id: ID do role
            role_data: Dados para atualização
            session: Sessão do banco de dados
            
        Returns:
            Role atualizado ou None se não encontrado
        """
        role = (await session.execute(
            select(Role).where(Role.id == role_id)
        )).scalar_one_or_none()
        
        if not role:
            return None
        
        # Verifica se novo nome já existe (se fornecido)
        if role_data.name and role_data.name != role.name:
            exists = (await session.execute(
                select(Role).where(Role.name == role_data.name)
            )).scalar_one_or_none()
            
            if exists:
                raise ValueError("Nome do role já existe")
        
        # Atualiza apenas campos fornecidos
        update_data = role_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(role, field, value)
        
        await session.commit()
        await session.refresh(role)
        
        return role

    @staticmethod
    async def delete_role(role_id: int, session: AsyncSession) -> bool:
        """Remove role (soft delete).
        
        Args:
            role_id: ID do role
            session: Sessão do banco de dados
            
        Returns:
            True se removido com sucesso
        """
        role = (await session.execute(
            select(Role).where(Role.id == role_id)
        )).scalar_one_or_none()
        
        if not role:
            return False
        
        role.is_active = False
        await session.commit()
        
        return True

    @staticmethod
    async def assign_permission_to_role(
        role_id: int,
        permission_id: int,
        session: AsyncSession
    ) -> bool:
        """Atribui permissão a um role.
        
        Args:
            role_id: ID do role
            permission_id: ID da permissão
            session: Sessão do banco de dados
            
        Returns:
            True se atribuído com sucesso
        """
        role = (await session.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )).scalar_one_or_none()
        
        permission = (await session.execute(
            select(Permission).where(Permission.id == permission_id)
        )).scalar_one_or_none()
        
        if not role or not permission:
            return False
        
        if permission not in role.permissions:
            role.permissions.append(permission)
            await session.commit()
        
        return True

    @staticmethod
    async def remove_permission_from_role(
        role_id: int,
        permission_id: int,
        session: AsyncSession
    ) -> bool:
        """Remove permissão de um role.
        
        Args:
            role_id: ID do role
            permission_id: ID da permissão
            session: Sessão do banco de dados
            
        Returns:
            True se removido com sucesso
        """
        role = (await session.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )).scalar_one_or_none()
        
        if not role:
            return False
        
        # Remove permissão se existir
        role.permissions = [p for p in role.permissions if p.id != permission_id]
        await session.commit()
        
        return True

    @staticmethod
    async def set_role_permissions(
        role_id: int,
        permission_ids: List[int],
        session: AsyncSession
    ) -> bool:
        """Define as permissões de um role (substitui todas).
        
        Args:
            role_id: ID do role
            permission_ids: IDs das permissões
            session: Sessão do banco de dados
            
        Returns:
            True se definido com sucesso
        """
        role = (await session.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )).scalar_one_or_none()
        
        if not role:
            return False
        
        # Busca as permissões
        permissions = (await session.execute(
            select(Permission).where(Permission.id.in_(permission_ids))
        )).scalars().all()
        
        # Define as permissões
        role.permissions = list(permissions)
        await session.commit()
        
        return True

    @staticmethod
    async def toggle_role_status(role_id: int, session: AsyncSession) -> Optional[Role]:
        """Alterna status ativo/inativo do role.
        
        Args:
            role_id: ID do role
            session: Sessão do banco de dados
            
        Returns:
            Role atualizado ou None se não encontrado
        """
        role = (await session.execute(
            select(Role).where(Role.id == role_id)
        )).scalar_one_or_none()


        if not role:
            return None

        role.is_active = not role.is_active
        await session.commit()
        await session.refresh(role)

        return role

    @staticmethod
    async def set_default_role(role_id: int, session: AsyncSession) -> bool:
        """Define um role como padrão (remove padrão dos outros).

        Args:
            role_id: ID do role
            session: Sessão do banco de dados
            
        Returns:
            True se definido com sucesso
        """
        role = (await session.execute(
            select(Role).where(Role.id == role_id)
        )).scalar_one_or_none()

        if not role:
            return False

        # Remove padrão de todos os roles
        all_roles = (await session.execute(select(Role))).scalars().all()
        for r in all_roles:
            r.is_default = False

        # Define o role como padrão
        role.is_default = True
        await session.commit()

        return True
