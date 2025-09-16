"""Configurações e fixtures para testes."""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_session
from app.models.user import User, Role
from app.models.permission import Permission
from app.core.security import get_password_hash
from app.services.permission_service import PermissionService


# URL do banco de teste em memória
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Engine de teste
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    echo=False,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = async_sessionmaker(
    test_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Cria um loop de eventos para toda a sessão de testes."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    """Cria uma sessão de teste isolada."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP para testes."""
    def override_get_session():
        return test_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession) -> User:
    """Cria um usuário de teste."""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_superuser(test_session: AsyncSession) -> User:
    """Cria um superusuário de teste."""
    user = User(
        email="admin@example.com",
        password_hash=get_password_hash("adminpass123"),
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_verified=True,
        is_superuser=True
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_permissions(test_session: AsyncSession) -> list[Permission]:
    """Cria permissões de teste."""
    await PermissionService.create_default_permissions(test_session)
    
    # Busca as permissões criadas
    from sqlalchemy import select
    result = await test_session.execute(select(Permission))
    permissions = list(result.scalars().all())
    return permissions


@pytest_asyncio.fixture
async def test_role(test_session: AsyncSession, test_permissions: list[Permission]) -> Role:
    """Cria um role de teste com algumas permissões."""
    role = Role(
        name="test_role",
        description="Role de teste",
        is_active=True
    )
    
    # Adiciona algumas permissões
    role.permissions = test_permissions[:3]  # Primeiras 3 permissões
    
    test_session.add(role)
    await test_session.commit()
    await test_session.refresh(role)
    return role


@pytest_asyncio.fixture
async def test_user_with_role(
    test_session: AsyncSession, 
    test_role: Role
) -> User:
    """Cria um usuário com role de teste."""
    user = User(
        email="roleuser@example.com",
        password_hash=get_password_hash("rolepass123"),
        first_name="Role",
        last_name="User",
        is_active=True,
        is_verified=True
    )
    
    user.roles = [test_role]
    
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict[str, str]:
    """Headers de autenticação para testes."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, test_superuser: User) -> dict[str, str]:
    """Headers de autenticação para admin."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_superuser.email,
            "password": "adminpass123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def role_user_headers(client: AsyncClient, test_user_with_role: User) -> dict[str, str]:
    """Headers de autenticação para usuário com role."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_with_role.email,
            "password": "rolepass123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Helpers para testes
class TestData:
    """Dados de teste reutilizáveis."""

    VALID_USER_DATA = {
        "email": "newuser@example.com",
        "password": "NewPass123!",
        "first_name": "New",
        "last_name": "User"
    }

    INVALID_USER_DATA = {
        "email": "invalid-email",
        "password": "weak",
        "first_name": "",
        "last_name": ""
    }

    VALID_ROLE_DATA = {
        "name": "new_role",
        "description": "New test role",
        "is_active": True
    }

    VALID_PERMISSION_DATA = {
        "name": "test:action",
        "description": "Test permission",
        "resource": "test",
        "action": "action"
    }
