"""Script para inicializar dados padrão do sistema."""
import asyncio
import os
import sys

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.db.session import AsyncSessionLocal
from app.services.permission_service import PermissionService
from app.services.role_service import RoleService


async def init_default_data():
    """Inicializa dados padrão do sistema."""
    async with AsyncSessionLocal() as session:
        try:
            print("🔧 Criando permissões padrão...")
            await PermissionService.create_default_permissions(session)
            print("✅ Permissões padrão criadas!")
            
            # Cria role padrão 'user' se não existir
            print("🔧 Verificando role padrão...")
            user_role = await RoleService.get_role_by_name("user", session)
            
            if not user_role:
                print("🔧 Criando role padrão 'user'...")
                from app.schemas.user import RoleCreate
                
                role_data = RoleCreate(
                    name="user",
                    description="Usuário padrão do sistema",
                    is_active=True,
                    is_default=True
                )
                
                user_role = await RoleService.create_role(role_data, session)
                print("✅ Role 'user' criado como padrão!")
            else:
                # Define como padrão se ainda não for
                if not user_role.is_default:
                    await RoleService.set_default_role(user_role.id, session)
                    print("✅ Role 'user' definido como padrão!")
                else:
                    print("✅ Role 'user' já existe e é padrão!")
            
            print("🎉 Inicialização de dados concluída!")
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(init_default_data())