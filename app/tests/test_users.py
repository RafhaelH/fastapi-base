"""Testes para gerenciamento de usu�rios."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.tests.conftest import TestData


class TestUsers:
    """Testes para endpoints de usu�rios."""

    @pytest.mark.asyncio
    async def test_list_users_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_user: User
    ):
        """Teste de listagem de usu�rios como admin."""
        response = await client.get("/api/v1/users/", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert isinstance(data["users"], list)
        assert data["total"] >= 1  # Pelo menos o test_user

    @pytest.mark.asyncio
    async def test_list_users_without_permission(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str]
    ):
        """Teste de listagem de usu�rios sem permiss�o."""
        response = await client.get("/api/v1/users/", headers=auth_headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_users_with_pagination(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de listagem com pagina��o."""
        response = await client.get(
            "/api/v1/users/?page=1&per_page=5", 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 5

    @pytest.mark.asyncio
    async def test_list_users_with_search(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_user: User
    ):
        """Teste de listagem com busca."""
        response = await client.get(
            f"/api/v1/users/?search={test_user.email}", 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        # Verifica se o usu�rio encontrado cont�m o email buscado
        found_user = next(
            (u for u in data["users"] if u["email"] == test_user.email), 
            None
        )
        assert found_user is not None

    @pytest.mark.asyncio
    async def test_get_user_by_id_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_user: User
    ):
        """Teste de obten��o de usu�rio por ID como admin."""
        response = await client.get(
            f"/api/v1/users/{test_user.id}", 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de obten��o de usu�rio inexistente."""
        response = await client.get("/api/v1/users/99999", headers=admin_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_own_user(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str],
        test_user: User
    ):
        """Teste de atualiza��o dos pr�prios dados."""
        response = await client.put(
            f"/api/v1/users/{test_user.id}",
            json={
                "first_name": "Updated",
                "last_name": "Name",
                "bio": "Updated bio"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["bio"] == "Updated bio"

    @pytest.mark.asyncio
    async def test_update_other_user_without_permission(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str],
        test_session: AsyncSession
    ):
        """Teste de atualiza��o de outro usu�rio sem permiss�o."""
        # Cria outro usu�rio
        from app.core.security import get_password_hash
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("password123"),
            first_name="Other",
            last_name="User"
        )
        test_session.add(other_user)
        await test_session.commit()
        await test_session.refresh(other_user)
        
        response = await client.put(
            f"/api/v1/users/{other_user.id}",
            json={"first_name": "Hacked"},
            headers=auth_headers
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_user_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_user: User
    ):
        """Teste de atualiza��o de usu�rio como admin."""
        response = await client.put(
            f"/api/v1/users/{test_user.id}",
            json={
                "first_name": "Admin Updated",
                "is_verified": True
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Admin Updated"
        assert data["is_verified"] is True

    @pytest.mark.asyncio
    async def test_delete_user_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_session: AsyncSession
    ):
        """Teste de desativa��o de usu�rio como admin."""
        # Cria usu�rio para deletar
        from app.core.security import get_password_hash
        user_to_delete = User(
            email="delete@example.com",
            password_hash=get_password_hash("password123"),
            first_name="Delete",
            last_name="Me"
        )
        test_session.add(user_to_delete)
        await test_session.commit()
        await test_session.refresh(user_to_delete)
        
        response = await client.delete(
            f"/api/v1/users/{user_to_delete.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert "desativado com sucesso" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_delete_user_without_permission(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str],
        test_user: User
    ):
        """Teste de desativa��o de usu�rio sem permiss�o."""
        response = await client.delete(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_toggle_user_status_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_user: User
    ):
        """Teste de altern�ncia de status de usu�rio como admin."""
        original_status = test_user.is_active
        
        response = await client.post(
            f"/api/v1/users/{test_user.id}/toggle-status",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is not original_status

    @pytest.mark.asyncio
    async def test_assign_roles_to_user(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_user: User,
        test_role
    ):
        """Teste de atribui��o de roles a usu�rio."""
        response = await client.post(
            f"/api/v1/users/{test_user.id}/roles",
            json={"role_ids": [test_role.id]},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert "atribu�dos com sucesso" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_remove_role_from_user(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_user_with_role: User,
        test_role
    ):
        """Teste de remo��o de role de usu�rio."""
        response = await client.delete(
            f"/api/v1/users/{test_user_with_role.id}/roles/{test_role.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert "removido com sucesso" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_list_users_filter_by_status(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_session: AsyncSession
    ):
        """Teste de filtro por status ativo."""
        # Cria usu�rio inativo
        from app.core.security import get_password_hash
        inactive_user = User(
            email="inactive@example.com",
            password_hash=get_password_hash("password123"),
            is_active=False
        )
        test_session.add(inactive_user)
        await test_session.commit()
        
        # Testa filtro por usu�rios ativos
        response = await client.get(
            "/api/v1/users/?is_active=true", 
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        for user in data["users"]:
            assert user["is_active"] is True
        
        # Testa filtro por usu�rios inativos
        response = await client.get(
            "/api/v1/users/?is_active=false", 
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        for user in data["users"]:
            assert user["is_active"] is False


class TestUserValidation:
    """Testes para valida��o de dados de usu�rio."""

    @pytest.mark.asyncio
    async def test_update_user_with_invalid_email(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str],
        test_user: User
    ):
        """Teste de atualiza��o com email inv�lido."""
        response = await client.put(
            f"/api/v1/users/{test_user.id}",
            json={"email": "invalid-email"},
            headers=auth_headers
        )
        
        # A valida��o pode retornar 422 (validation error) ou 400 (bad request)
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_update_user_with_long_name(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str],
        test_user: User
    ):
        """Teste de atualiza��o com nome muito longo."""
        long_name = "a" * 101  # Excede limite de 100 caracteres
        
        response = await client.put(
            f"/api/v1/users/{test_user.id}",
            json={"first_name": long_name},
            headers=auth_headers
        )
        
        assert response.status_code == 422