"""Serviços para autenticação e gerenciamento de usuários."""
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User, Role
from app.core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    get_password_hash,
    verify_token
)
from app.schemas.auth import Token


class AuthService:
    """Serviço para operações de autenticação."""
    
    @staticmethod
    async def authenticate(email: str, password: str, session: AsyncSession) -> Optional[Token]:
        """Autentica um usuário com email e senha.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            session: Sessão do banco de dados
            
        Returns:
            Token de acesso se autenticado, None caso contrário
        """
        # Busca o usuário com roles e permissões
        user = (await session.execute(
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.email == email)
        )).scalar_one_or_none()
        
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            return None
        
        # Coleta permissões do usuário
        permissions = []
        for role in user.roles:
            if role.is_active:
                for permission in role.permissions:
                    if permission.is_active:
                        permissions.append(f"{permission.resource}:{permission.action}")
        
        # Remove duplicatas
        permissions = list(set(permissions))
        
        # Cria tokens
        access_token = create_access_token(
            subject=user.email,
            permissions=permissions
        )
        refresh_token = create_refresh_token(subject=user.email)
        
        # Atualiza last_login
        user.last_login = datetime.utcnow()
        await session.commit()
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=3600  # 1 hora
        )

    @staticmethod
    async def register(
        email: str, 
        password: str, 
        session: AsyncSession,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None
    ) -> User:
        """Registra um novo usuário.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            session: Sessão do banco de dados
            first_name: Nome do usuário
            last_name: Sobrenome do usuário
            phone: Telefone do usuário
            
        Returns:
            Usuário criado
            
        Raises:
            ValueError: Se email já existir
        """
        # Verifica se email já existe
        exists = (await session.execute(
            select(User).where(User.email == email)
        )).scalar_one_or_none()
        
        if exists:
            raise ValueError("Email já cadastrado")
        
        # Cria o usuário
        new_user = User(
            email=email,
            password_hash=get_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        
        # Atribui role padrão se existir
        default_role = (await session.execute(
            select(Role).where(Role.is_default == True, Role.is_active == True)
        )).scalar_one_or_none()
        
        if default_role:
            new_user.roles.append(default_role)
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        return new_user

    @staticmethod
    async def refresh_token(refresh_token: str, session: AsyncSession) -> Optional[Token]:
        """Gera um novo token de acesso usando refresh token.
        
        Args:
            refresh_token: Refresh token válido
            session: Sessão do banco de dados
            
        Returns:
            Novo token de acesso se válido, None caso contrário
        """
        try:
            # Verifica o refresh token
            token_payload = verify_token(refresh_token)
            
            # Busca o usuário
            user = (await session.execute(
                select(User)
                .options(selectinload(User.roles).selectinload(Role.permissions))
                .where(User.email == token_payload.sub)
            )).scalar_one_or_none()
            
            if not user or not user.is_active:
                return None
            
            # Coleta permissões
            permissions = []
            for role in user.roles:
                if role.is_active:
                    for permission in role.permissions:
                        if permission.is_active:
                            permissions.append(f"{permission.resource}:{permission.action}")
            
            permissions = list(set(permissions))
            
            # Cria novo access token
            access_token = create_access_token(
                subject=user.email,
                permissions=permissions
            )
            
            return Token(
                access_token=access_token,
                refresh_token=refresh_token,  # Mantém o mesmo refresh token
                expires_in=3600
            )
            
        except Exception:
            return None

    @staticmethod
    async def change_password(
        user: User,
        current_password: str,
        new_password: str,
        session: AsyncSession
    ) -> bool:
        """Altera a senha do usuário.
        
        Args:
            user: Usuário
            current_password: Senha atual
            new_password: Nova senha
            session: Sessão do banco de dados
            
        Returns:
            True se alterada com sucesso, False caso contrário
        """
        if not verify_password(current_password, user.password_hash):
            return False
        
        user.password_hash = get_password_hash(new_password)
        await session.commit()
        
        return True

    @staticmethod
    async def get_user_permissions(user: User) -> list[str]:
        """Obtém todas as permissões de um usuário.
        
        Args:
            user: Usuário
            
        Returns:
            Lista de permissões no formato 'resource:action'
        """
        if user.is_superuser:
            return ["*:*"]  # Superuser tem todas as permissões
        
        permissions = []
        for role in user.roles:
            if role.is_active:
                for permission in role.permissions:
                    if permission.is_active:
                        permissions.append(f"{permission.resource}:{permission.action}")
        
        return list(set(permissions))
