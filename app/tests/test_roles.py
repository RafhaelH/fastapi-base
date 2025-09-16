"""Testes para gerenciamento de roles."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Role
from app.models.permission import Permission
from app.tests.conftest import TestData


class TestRoles:
    """Testes para endpoints de roles."""

    @pytest.mark.asyncio
    async def test_list_roles_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_role: Role
    ):
        """Teste de listagem de roles como admin."""
        response = await client.get("/api/v1/roles/", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "roles" in data
        assert "total" in data
        assert isinstance(data["roles"], list)
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_roles_without_permission(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str]
    ):
        """Teste de listagem de roles sem permissão."""
        response = await client.get("/api/v1/roles/", headers=auth_headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_role_by_id_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_role: Role
    ):
        """Teste de obtenção de role por ID como admin."""
        response = await client.get(
            f"/api/v1/roles/{test_role.id}", 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_role.id
        assert data["name"] == test_role.name
        assert data["description"] == test_role.description

    @pytest.mark.asyncio
    async def test_get_role_by_id_not_found(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de obtenção de role inexistente."""
        response = await client.get("/api/v1/roles/99999", headers=admin_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_role_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de criação de role como admin."""
        response = await client.post(
            "/api/v1/roles/",
            json=TestData.VALID_ROLE_DATA,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == TestData.VALID_ROLE_DATA["name"]
        assert data["description"] == TestData.VALID_ROLE_DATA["description"]
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_role_duplicate_name(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_role: Role
    ):
        """Teste de criação de role com nome duplicado."""
        response = await client.post(
            "/api/v1/roles/",
            json={
                "name": test_role.name,
                "description": "Duplicate role"
            },
            headers=admin_headers
        )
        
        assert response.status_code == 400
        assert "já existe" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_role_without_permission(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str]
    ):
        """Teste de criação de role sem permissão."""
        response = await client.post(
            "/api/v1/roles/",
            json=TestData.VALID_ROLE_DATA,
            headers=auth_headers
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_role_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_role: Role
    ):
        """Teste de atualização de role como admin."""
        response = await client.put(
            f"/api/v1/roles/{test_role.id}",
            json={
                "description": "Updated description",
                "is_active": True
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_role_not_found(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de atualização de role inexistente."""
        response = await client.put(
            "/api/v1/roles/99999",
            json={"description": "New description"},
            headers=admin_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_role_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_session: AsyncSession
    ):
        """Teste de desativação de role como admin."""
        # Cria role para deletar
        role_to_delete = Role(
            name="delete_role",
            description="Role to be deleted"
        )
        test_session.add(role_to_delete)
        await test_session.commit()
        await test_session.refresh(role_to_delete)
        
        response = await client.delete(
            f"/api/v1/roles/{role_to_delete.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert "desativado com sucesso" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_toggle_role_status_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_role: Role
    ):
        """Teste de alternância de status de role como admin."""
        original_status = test_role.is_active
        
        response = await client.post(
            f"/api/v1/roles/{test_role.id}/toggle-status",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is not original_status

    @pytest.mark.asyncio
    async def test_set_role_permissions(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_role: Role,
        test_permissions: list[Permission]
    ):
        """Teste de definição de permissões do role."""
        permission_ids = [p.id for p in test_permissions[:2]]  # Primeiras 2 permissões
        
        response = await client.post(
            f"/api/v1/roles/{test_role.id}/permissions",
            json={"permission_ids": permission_ids},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert "definidas com sucesso" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_add_permission_to_role(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_role: Role,
        test_permissions: list[Permission]
    ):
        """Teste de adição de permissão específica ao role."""
        permission = test_permissions[0]
        
        response = await client.post(
            f"/api/v1/roles/{test_role.id}/permissions/{permission.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert "adicionada com sucesso" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_remove_permission_from_role(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_role: Role,
        test_permissions: list[Permission]
    ):
        """Teste de remoção de permissão específica do role."""
        # Assume que test_role já tem algumas permissões
        if test_role.permissions:
            permission = test_role.permissions[0]
            
            response = await client.delete(
                f"/api/v1/roles/{test_role.id}/permissions/{permission.id}",
                headers=admin_headers
            )
            
            assert response.status_code == 200
            assert "removida com sucesso" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_set_default_role(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_role: Role
    ):
        """Teste de definição de role como padrão."""
        response = await client.post(
            f"/api/v1/roles/{test_role.id}/set-default",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert "definido como padrão" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_list_roles_with_search(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_role: Role
    ):
        """Teste de listagem com busca."""
        response = await client.get(
            f"/api/v1/roles/?search={test_role.name}", 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        found_role = next(
            (r for r in data["roles"] if r["name"] == test_role.name), 
            None
        )
        assert found_role is not None

    @pytest.mark.asyncio
    async def test_list_roles_filter_by_status(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_session: AsyncSession
    ):
        """Teste de filtro por status ativo."""
        # Cria role inativo
        inactive_role = Role(
            name="inactive_role",
            description="Inactive role",
            is_active=False
        )
        test_session.add(inactive_role)
        await test_session.commit()
        
        # Testa filtro por roles ativos
        response = await client.get(
            "/api/v1/roles/?is_active=true", 
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        for role in data["roles"]:
            assert role["is_active"] is True
        
        # Testa filtro por roles inativos
        response = await client.get(
            "/api/v1/roles/?is_active=false", 
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        for role in data["roles"]:
            assert role["is_active"] is False


class TestRoleValidation:
    """Testes para validação de dados de role."""

    @pytest.mark.asyncio
    async def test_create_role_with_invalid_data(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de criação de role com dados inválidos."""
        response = await client.post(
            "/api/v1/roles/",
            json={
                "name": "",  # Nome vazio
                "description": "a" * 201  # Descrição muito longa
            },
            headers=admin_headers
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_role_with_long_name(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_role: Role
    ):
        """Teste de atualização com nome muito longo."""
        long_name = "a" * 51  # Excede limite de 50 caracteres
        
        response = await client.put(
            f"/api/v1/roles/{test_role.id}",
            json={"name": long_name},
            headers=admin_headers
        )
        
        assert response.status_code == 422