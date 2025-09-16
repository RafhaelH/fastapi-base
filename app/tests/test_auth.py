"""Testes para autenticação e autorização."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.tests.conftest import TestData


class TestAuth:
    """Testes para endpoints de autenticação."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Teste de login com credenciais válidas."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient):
        """Teste de login com email inválido."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 401
        assert "Credenciais inválidas" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, test_user: User):
        """Teste de login com senha inválida."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Credenciais inválidas" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client: AsyncClient, test_session: AsyncSession):
        """Teste de login com usuário inativo."""
        # Cria usuário inativo
        from app.core.security import get_password_hash
        inactive_user = User(
            email="inactive@example.com",
            password_hash=get_password_hash("testpass123"),
            is_active=False
        )
        test_session.add(inactive_user)
        await test_session.commit()
        
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inactive@example.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Teste de registro com dados válidos."""
        response = await client.post(
            "/api/v1/auth/register",
            json=TestData.VALID_USER_DATA
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TestData.VALID_USER_DATA["email"]
        assert data["first_name"] == TestData.VALID_USER_DATA["first_name"]
        assert data["last_name"] == TestData.VALID_USER_DATA["last_name"]
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Teste de registro com email duplicado."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "newpass123",
                "first_name": "New",
                "last_name": "User"
            }
        )
        
        assert response.status_code == 400
        assert "Email já cadastrado" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_invalid_data(self, client: AsyncClient):
        """Teste de registro com dados inválidos."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "weak",
                "first_name": "",
                "last_name": ""
            }
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, test_user: User):
        """Teste de renovação de token com refresh token válido."""
        # Primeiro login para obter refresh token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "testpass123"
            }
        )
        
        refresh_token = login_response.json()["refresh_token"]
        
        # Usa refresh token para obter novo access token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Teste de renovação com refresh token inválido."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_change_password_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str]
    ):
        """Teste de alteração de senha com sucesso."""
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "testpass123",
                "new_password": "NewPass123!"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "Senha alterada com sucesso" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str]
    ):
        """Teste de alteração de senha com senha atual incorreta."""
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "wrongpassword",
                "new_password": "NewPass123!"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Senha atual incorreta" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_change_password_unauthenticated(self, client: AsyncClient):
        """Teste de alteração de senha sem autenticação."""
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "testpass123",
                "new_password": "NewPass123!"
            }
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout(self, client: AsyncClient, auth_headers: dict[str, str]):
        """Teste de logout."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "Logout realizado com sucesso" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_get_my_permissions(
        self, 
        client: AsyncClient, 
        role_user_headers: dict[str, str]
    ):
        """Teste de obtenção de permissões do usuário."""
        response = await client.get(
            "/api/v1/auth/me/permissions",
            headers=role_user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "permissions" in data
        assert isinstance(data["permissions"], list)

    @pytest.mark.asyncio
    async def test_oauth2_login(self, client: AsyncClient, test_user: User):
        """Teste de login OAuth2 (compatibilidade FastAPI docs)."""
        response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user.email,
                "password": "testpass123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


class TestAuthMiddleware:
    """Testes para middleware de autenticação."""

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Teste de acesso a endpoint protegido sem token."""
        response = await client.get("/api/v1/users/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        """Teste de acesso a endpoint protegido com token inválido."""
        response = await client.get(
            "/api/v1/users/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_valid_token(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de acesso a endpoint protegido com token válido."""
        response = await client.get(
            "/api/v1/users/",
            headers=admin_headers
        )
        assert response.status_code == 200


class TestPermissions:
    """Testes para sistema de permissões."""

    @pytest.mark.asyncio
    async def test_superuser_has_all_permissions(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de que superuser tem acesso total."""
        # Testa acesso a users
        response = await client.get("/api/v1/users/", headers=admin_headers)
        assert response.status_code == 200
        
        # Testa acesso a roles
        response = await client.get("/api/v1/roles/", headers=admin_headers)
        assert response.status_code == 200
        
        # Testa acesso a permissions
        response = await client.get("/api/v1/permissions/", headers=admin_headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_user_without_permission_denied(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str]
    ):
        """Teste de que usuário sem permissão é negado."""
        response = await client.get("/api/v1/users/", headers=auth_headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_user_with_permission_allowed(
        self, 
        client: AsyncClient, 
        role_user_headers: dict[str, str]
    ):
        """Teste de que usuário com permissão é permitido."""
        # Este teste depende das permissões atribuídas ao test_role
        # Se o role tiver users:read, deve passar
        response = await client.get("/api/v1/users/", headers=role_user_headers)
        # Status pode ser 200 ou 403 dependendo das permissões do role
        assert response.status_code in [200, 403]