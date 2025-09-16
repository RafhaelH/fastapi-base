"""Serviços para gerenciamento de usuários."""
from math import ceil
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.models.user import User, Role
from app.schemas.user import UserUpdate, UserList
from app.core.security import get_password_hash


class UserService:
    """Serviço para operações com usuários."""
    
    @staticmethod
    async def get_all_users(
        session: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> UserList:
        """Lista usuários com paginação e filtros.
        
        Args:
            session: Sessão do banco de dados
            page: Página atual (1-indexed)
            per_page: Itens por página
            search: Termo de busca (email, nome)
            is_active: Filtro por status ativo
            
        Returns:
            Lista paginada de usuários
        """
        query = select(User).options(selectinload(User.roles))
        
        # Aplicar filtros
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term)
                )
            )
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        # Contagem total
        count_query = select(func.count(User.id))
        if search:
            search_term = f"%{search}%"
            count_query = count_query.where(
                or_(
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term)
                )
            )
        if is_active is not None:
            count_query = count_query.where(User.is_active == is_active)
        
        total = (await session.execute(count_query)).scalar()
        
        # Paginação
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        # Ordenação
        query = query.order_by(User.created_at.desc())
        
        result = await session.execute(query)
        users = list(result.scalars().all())
        
        return UserList(
            users=users,
            total=total,
            page=page,
            per_page=per_page,
            pages=ceil(total / per_page) if total > 0 else 1
        )

    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession) -> Optional[User]:
        """Obtém usuário por ID.
        
        Args:
            user_id: ID do usuário
            session: Sessão do banco de dados
            
        Returns:
            Usuário encontrado ou None
        """
        return (await session.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.id == user_id)
        )).scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(email: str, session: AsyncSession) -> Optional[User]:
        """Obtém usuário por email.
        
        Args:
            email: Email do usuário
            session: Sessão do banco de dados
            
        Returns:
            Usuário encontrado ou None
        """
        return (await session.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.email == email)
        )).scalar_one_or_none()

    @staticmethod
    async def update_user(
        user_id: int,
        user_data: UserUpdate,
        session: AsyncSession
    ) -> Optional[User]:
        """Atualiza dados do usuário.
        
        Args:
            user_id: ID do usuário
            user_data: Dados para atualização
            session: Sessão do banco de dados
            
        Returns:
            Usuário atualizado ou None se não encontrado
        """
        user = (await session.execute(
            select(User).where(User.id == user_id)
        )).scalar_one_or_none()
        
        if not user:
            return None
        
        # Atualiza apenas campos fornecidos
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await session.commit()
        await session.refresh(user)
        
        return user

    @staticmethod
    async def delete_user(user_id: int, session: AsyncSession) -> bool:
        """Remove usuário (soft delete).
        
        Args:
            user_id: ID do usuário
            session: Sessão do banco de dados
            
        Returns:
            True se removido com sucesso
        """
        user = (await session.execute(
            select(User).where(User.id == user_id)
        )).scalar_one_or_none()
        
        if not user:
            return False
        
        user.is_active = False
        await session.commit()
        
        return True

    @staticmethod
    async def assign_role_to_user(
        user_id: int,
        role_id: int,
        session: AsyncSession
    ) -> bool:
        """Atribui role a um usuário.
        
        Args:
            user_id: ID do usuário
            role_id: ID do role
            session: Sessão do banco de dados
            
        Returns:
            True se atribuído com sucesso
        """
        user = (await session.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )).scalar_one_or_none()
        
        role = (await session.execute(
            select(Role).where(Role.id == role_id)
        )).scalar_one_or_none()
        
        if not user or not role:
            return False
        
        if role not in user.roles:
            user.roles.append(role)
            await session.commit()
        
        return True

    @staticmethod
    async def remove_role_from_user(
        user_id: int,
        role_id: int,
        session: AsyncSession
    ) -> bool:
        """Remove role de um usuário.
        
        Args:
            user_id: ID do usuário
            role_id: ID do role
            session: Sessão do banco de dados
            
        Returns:
            True se removido com sucesso
        """
        user = (await session.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )).scalar_one_or_none()
        
        if not user:
            return False
        
        # Remove role se existir
        user.roles = [role for role in user.roles if role.id != role_id]
        await session.commit()
        
        return True

    @staticmethod
    async def toggle_user_status(user_id: int, session: AsyncSession) -> Optional[User]:
        """Alterna status ativo/inativo do usuário.
        
        Args:
            user_id: ID do usuário
            session: Sessão do banco de dados
            
        Returns:
            Usuário atualizado ou None se não encontrado
        """
        user = (await session.execute(
            select(User).where(User.id == user_id)
        )).scalar_one_or_none()
        
        if not user:
            return None
        
        user.is_active = not user.is_active
        await session.commit()
        await session.refresh(user)
        
        return user
