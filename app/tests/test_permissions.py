"""Testes para gerenciamento de permissões."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.tests.conftest import TestData


class TestPermissions:
    """Testes para endpoints de permissões."""

    @pytest.mark.asyncio
    async def test_list_permissions_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_permissions: list[Permission]
    ):
        """Teste de listagem de permissões como admin."""
        response = await client.get("/api/v1/permissions/", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "permissions" in data
        assert "total" in data
        assert isinstance(data["permissions"], list)
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_permissions_without_permission(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str]
    ):
        """Teste de listagem de permissões sem permissão."""
        response = await client.get("/api/v1/permissions/", headers=auth_headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_permissions_with_pagination(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de listagem com paginação."""
        response = await client.get(
            "/api/v1/permissions/?page=1&per_page=5", 
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 5

    @pytest.mark.asyncio
    async def test_list_permissions_with_filters(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_permissions: list[Permission]
    ):
        """Teste de listagem com filtros."""
        if test_permissions:
            permission = test_permissions[0]
            
            # Filtro por recurso
            response = await client.get(
                f"/api/v1/permissions/?resource={permission.resource}", 
                headers=admin_headers
            )
            assert response.status_code == 200
            data = response.json()
            for perm in data["permissions"]:
                assert perm["resource"] == permission.resource
            
            # Filtro por ação
            response = await client.get(
                f"/api/v1/permissions/?action={permission.action}", 
                headers=admin_headers
            )
            assert response.status_code == 200
            data = response.json()
            for perm in data["permissions"]:
                assert perm["action"] == permission.action

    @pytest.mark.asyncio
    async def test_list_permissions_with_search(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_permissions: list[Permission]
    ):
        """Teste de listagem com busca."""
        if test_permissions:
            permission = test_permissions[0]
            
            response = await client.get(
                f"/api/v1/permissions/?search={permission.name}", 
                headers=admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_permission_by_id_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_permissions: list[Permission]
    ):
        """Teste de obtenção de permissão por ID como admin."""
        if test_permissions:
            permission = test_permissions[0]
            
            response = await client.get(
                f"/api/v1/permissions/{permission.id}", 
                headers=admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == permission.id
            assert data["name"] == permission.name
            assert data["resource"] == permission.resource
            assert data["action"] == permission.action

    @pytest.mark.asyncio
    async def test_get_permission_by_id_not_found(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de obtenção de permissão inexistente."""
        response = await client.get("/api/v1/permissions/99999", headers=admin_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_permission_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de criação de permissão como admin."""
        response = await client.post(
            "/api/v1/permissions/",
            json=TestData.VALID_PERMISSION_DATA,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == TestData.VALID_PERMISSION_DATA["name"]
        assert data["resource"] == TestData.VALID_PERMISSION_DATA["resource"]
        assert data["action"] == TestData.VALID_PERMISSION_DATA["action"]

    @pytest.mark.asyncio
    async def test_create_permission_duplicate_name(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_permissions: list[Permission]
    ):
        """Teste de criação de permissão com nome duplicado."""
        if test_permissions:
            permission = test_permissions[0]
            
            response = await client.post(
                "/api/v1/permissions/",
                json={
                    "name": permission.name,
                    "description": "Duplicate permission",
                    "resource": "new_resource",
                    "action": "new_action"
                },
                headers=admin_headers
            )
            
            assert response.status_code == 400
            assert "já existe" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_permission_duplicate_resource_action(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_permissions: list[Permission]
    ):
        """Teste de criação de permissão com combinação recurso/ação duplicada."""
        if test_permissions:
            permission = test_permissions[0]
            
            response = await client.post(
                "/api/v1/permissions/",
                json={
                    "name": "new_permission_name",
                    "description": "New permission",
                    "resource": permission.resource,
                    "action": permission.action
                },
                headers=admin_headers
            )
            
            assert response.status_code == 400
            assert "Combinação recurso/ação já existe" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_permission_without_permission(
        self, 
        client: AsyncClient, 
        auth_headers: dict[str, str]
    ):
        """Teste de criação de permissão sem permissão."""
        response = await client.post(
            "/api/v1/permissions/",
            json=TestData.VALID_PERMISSION_DATA,
            headers=auth_headers
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_permission_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_permissions: list[Permission]
    ):
        """Teste de atualização de permissão como admin."""
        if test_permissions:
            permission = test_permissions[0]
            
            response = await client.put(
                f"/api/v1/permissions/{permission.id}",
                json={
                    "description": "Updated description"
                },
                headers=admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_permission_not_found(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de atualização de permissão inexistente."""
        response = await client.put(
            "/api/v1/permissions/99999",
            json={"description": "New description"},
            headers=admin_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_permission_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_session: AsyncSession
    ):
        """Teste de desativação de permissão como admin."""
        # Cria permissão para deletar
        permission_to_delete = Permission(
            name="delete:permission",
            description="Permission to be deleted",
            resource="delete",
            action="permission"
        )
        test_session.add(permission_to_delete)
        await test_session.commit()
        await test_session.refresh(permission_to_delete)
        
        response = await client.delete(
            f"/api/v1/permissions/{permission_to_delete.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert "desativada com sucesso" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_toggle_permission_status_as_admin(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_permissions: list[Permission]
    ):
        """Teste de alternância de status de permissão como admin."""
        if test_permissions:
            permission = test_permissions[0]
            original_status = permission.is_active
            
            response = await client.post(
                f"/api/v1/permissions/{permission.id}/toggle-status",
                headers=admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_active"] is not original_status

    @pytest.mark.asyncio
    async def test_list_resources(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_permissions: list[Permission]
    ):
        """Teste de listagem de recursos únicos."""
        response = await client.get("/api/v1/permissions/resources", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "resources" in data
        assert isinstance(data["resources"], list)

    @pytest.mark.asyncio
    async def test_list_actions(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_permissions: list[Permission]
    ):
        """Teste de listagem de ações únicas."""
        response = await client.get("/api/v1/permissions/actions", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "actions" in data
        assert isinstance(data["actions"], list)

    @pytest.mark.asyncio
    async def test_create_default_permissions(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de criação de permissões padrão."""
        response = await client.post(
            "/api/v1/permissions/create-defaults",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert "criadas com sucesso" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_list_permissions_filter_by_status(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_session: AsyncSession
    ):
        """Teste de filtro por status ativo."""
        # Cria permissão inativa
        inactive_permission = Permission(
            name="inactive:permission",
            description="Inactive permission",
            resource="inactive",
            action="permission",
            is_active=False
        )
        test_session.add(inactive_permission)
        await test_session.commit()
        
        # Testa filtro por permissões ativas
        response = await client.get(
            "/api/v1/permissions/?is_active=true", 
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        for permission in data["permissions"]:
            assert permission["is_active"] is True
        
        # Testa filtro por permissões inativas
        response = await client.get(
            "/api/v1/permissions/?is_active=false", 
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        for permission in data["permissions"]:
            assert permission["is_active"] is False


class TestPermissionValidation:
    """Testes para validação de dados de permissão."""

    @pytest.mark.asyncio
    async def test_create_permission_with_invalid_data(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str]
    ):
        """Teste de criação de permissão com dados inválidos."""
        response = await client.post(
            "/api/v1/permissions/",
            json={
                "name": "",  # Nome vazio
                "description": "a" * 201,  # Descrição muito longa
                "resource": "",  # Recurso vazio
                "action": ""  # Ação vazia
            },
            headers=admin_headers
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_permission_with_long_fields(
        self, 
        client: AsyncClient, 
        admin_headers: dict[str, str],
        test_permissions: list[Permission]
    ):
        """Teste de atualização com campos muito longos."""
        if test_permissions:
            permission = test_permissions[0]
            
            response = await client.put(
                f"/api/v1/permissions/{permission.id}",
                json={
                    "name": "a" * 101,  # Excede limite de 100 caracteres
                    "resource": "a" * 51,  # Excede limite de 50 caracteres
                    "action": "a" * 21  # Excede limite de 20 caracteres
                },
                headers=admin_headers
            )
            
            assert response.status_code == 422