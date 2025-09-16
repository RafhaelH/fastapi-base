# FastAPI Base - Sistema de Autenticação e RBAC

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-blue?style=for-the-badge&logo=docker&logoColor=white)

**Sistema FastAPI robusto com autenticação JWT e controle de acesso baseado em funções (RBAC)**

[📚 Documentação](#documentação) • [🚀 Quick Start](#quick-start) • [🔧 Configuração](#configuração) • [📖 API Reference](#api-reference)

</div>

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#️arquitetura)
- [Quick Start](#quick-start)
- [Configuração](#configuração)
- [API Reference](#api-reference)
- [Estrutura do Projeto](#️estrutura-do-projeto)
- [Testes](#testes)
- [Documentação](#documentação)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## Sobre o Projeto

**FastAPI Base** é um sistema completo de backend construído com FastAPI, fornecendo uma base sólida para aplicações que necessitam de autenticação segura e controle de acesso granular. O projeto implementa as melhores práticas de segurança e arquitetura, oferecendo um sistema RBAC (Role-Based Access Control) robusto e escalável.

### **Por que usar este projeto?**

- ✅ **Autenticação JWT segura** com refresh tokens
- ✅ **Sistema RBAC completo** (Usuários → Roles → Permissões)
- ✅ **Arquitetura limpa** e bem estruturada
- ✅ **Pronto para produção** com Docker e health checks
- ✅ **Escalável** com Celery e Redis
- ✅ **Bem documentado** com OpenAPI/Swagger
- ✅ **Testes incluídos** com pytest
- ✅ **Type hints** completos com Pydantic

---

## Funcionalidades

### **Autenticação & Segurança**
- **JWT Authentication** com access e refresh tokens
- **Registro e login** de usuários
- **Reset de senha** via email com templates HTML
- **Verificação de email** (pronto para implementar)
- **Validação robusta** de senhas com critérios de segurança
- **Rate limiting** preparado com slowapi

### **Sistema RBAC (Role-Based Access Control)**
- **Gestão completa de usuários** com perfis detalhados
- **Sistema de roles** flexível e configurável
- **Permissões granulares** no formato `resource:action`
- **Soft delete** para todos os recursos
- **Auditoria completa** com timestamps

### **Recursos Avançados**
- **Paginação inteligente** em todas as listagens
- **Filtros de busca** avançados
- **Health checks** para monitoramento
- **Tarefas assíncronas** com Celery
- **Sistema de email** com templates Jinja2
- **Middleware de segurança** configurável

### **Banco de Dados & Cache**
- **PostgreSQL** com SQLAlchemy 2.0 assíncrono
- **Migrações automáticas** com Alembic
- **Redis** para cache e broker do Celery
- **Pool de conexões** otimizado

---

## Arquitetura

```mermaid
graph TB
    A[FastAPI App] --> B[Auth Middleware]
    B --> C[API Routes]
    C --> D[Services Layer]
    D --> E[SQLAlchemy Models]
    E --> F[PostgreSQL]

    C --> G[Celery Tasks]
    G --> H[Redis]
    H --> I[Email Service]

    J[Frontend] --> A
    K[Health Checks] --> A
    L[Docker Compose] --> A
    L --> F
    L --> H
```

### **Camadas da Aplicação**

| Camada | Responsabilidade | Tecnologias |
|--------|------------------|-------------|
| **API** | Endpoints REST e validação | FastAPI, Pydantic |
| **Services** | Lógica de negócio | Python, SQLAlchemy |
| **Models** | Modelos de dados | SQLAlchemy ORM |
| **Database** | Persistência | PostgreSQL |
| **Cache** | Cache e filas | Redis |
| **Tasks** | Processamento assíncrono | Celery |
| **Auth** | Autenticação e autorização | JWT, BCrypt |

---

## Quick Start

### **Pré-requisitos**

- Python 3.12+
- Docker e Docker Compose
- Git

### **Instalação Rápida**

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd fastapi-base

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 3. Execute com Docker
docker-compose up -d

# 4. Aguarde a inicialização (1-2 minutos)
docker-compose logs -f api

# 5. Acesse a documentação
open http://localhost:8000/api/v1/docs
```

### **Verificação da Instalação**

```bash
# Verificar se todos os serviços estão funcionando
curl http://localhost:8000/health

# Resposta esperada:
# {"status": "healthy", "timestamp": "..."}
```

---

## Configuração

### **Variáveis de Ambiente**

Copie o arquivo `.env.example` para `.env` e configure:

```bash
# Configurações da Aplicação
PROJECT_NAME=FastAPI Base
ENV=development
DEBUG=true
SECRET_KEY=sua_chave_secreta_super_segura_aqui_com_pelo_menos_32_caracteres

# API
API_V1_PREFIX=/api/v1

# Database
POSTGRES_DB=fastapi_base
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (Gmail exemplo)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seuemail@gmail.com
SMTP_PASSWORD=senha_de_app_do_gmail
EMAIL_FROM=seuemail@gmail.com
```

### **Configuração Docker**

O projeto está configurado para funcionar out-of-the-box com Docker Compose:

```yaml
services:
  api:        # Aplicação FastAPI
  db:         # PostgreSQL 16
  redis:      # Redis 7
  worker:     # Celery Worker
```

### **Configuração de Email**

Para habilitar o envio de emails (reset de senha):

1. **Gmail**: Use senhas de aplicativo
2. **Outros provedores**: Configure SMTP_SERVER, SMTP_PORT
3. **Desenvolvimento**: Use MailHog ou similar

---

## API Reference

### **Autenticação**

| Endpoint | Método | Descrição | Auth |
|----------|--------|-----------|------|
| `/auth/login` | POST | Login com email/senha | ❌ |
| `/auth/register` | POST | Registrar novo usuário | ❌ |
| `/auth/refresh` | POST | Renovar access token | ❌ |
| `/auth/logout` | POST | Logout do usuário | ✅ |
| `/auth/change-password` | POST | Alterar senha | ✅ |
| `/auth/password-reset` | POST | Solicitar reset de senha | ❌ |
| `/auth/password-reset/confirm` | POST | Confirmar reset de senha | ❌ |

### **Usuários**

| Endpoint | Método | Descrição | Permissão |
|----------|--------|-----------|-----------|
| `/users/` | GET | Listar usuários | `users:read` |
| `/users/{id}` | GET | Obter usuário | `users:read` |
| `/users/{id}` | PUT | Atualizar usuário | `users:write` |
| `/users/{id}` | DELETE | Desativar usuário | `users:delete` |
| `/users/{id}/roles` | POST | Atribuir roles | `users:write` |

### **Roles**

| Endpoint | Método | Descrição | Permissão |
|----------|--------|-----------|-----------|
| `/roles/` | GET | Listar roles | `roles:read` |
| `/roles/{id}` | GET | Obter role | `roles:read` |
| `/roles/` | POST | Criar role | `roles:write` |
| `/roles/{id}` | PUT | Atualizar role | `roles:write` |
| `/roles/{id}` | DELETE | Desativar role | `roles:delete` |

### **Permissões**

| Endpoint | Método | Descrição | Permissão |
|----------|--------|-----------|-----------|
| `/permissions/` | GET | Listar permissões | `permissions:read` |
| `/permissions/` | POST | Criar permissão | `permissions:write` |
| `/permissions/create-defaults` | POST | Criar permissões padrão | `admin:access` |

### **Sistema**

| Endpoint | Método | Descrição | Auth |
|----------|--------|-----------|------|
| `/health` | GET | Status da aplicação | ❌ |
| `/health/detailed` | GET | Status com dependências | ❌ |
| `/` | GET | Informações básicas | ❌ |
| `/info` | GET | Informações detalhadas | ❌ |

### **Exemplos de Uso**

#### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@exemplo.com",
    "password": "MinhaSenh@123"
  }'
```

#### Listar Usuários (com autenticação)
```bash
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

---

## Estrutura do Projeto

```
fastapi-base/
├── 📁 alembic/                 # Migrações do banco
│   ├── versions/               # Arquivos de migração
│   └── env.py                  # Configuração Alembic
├── 📁 app/                     # Aplicação principal
│   ├── 📁 api/                 # Camada de API
│   │   ├── 📁 routes/          # Endpoints organizados
│   │   │   ├── auth.py         # Autenticação
│   │   │   ├── users.py        # Usuários
│   │   │   ├── roles.py        # Roles
│   │   │   ├── permissions.py  # Permissões
│   │   │   ├── me.py           # Perfil do usuário
│   │   │   └── health.py       # Health checks
│   │   └── deps.py             # Dependências de auth
│   ├── 📁 core/                # Configurações centrais
│   │   ├── config.py           # Settings da aplicação
│   │   ├── security.py         # Utilitários de segurança
│   │   └── logging.py          # Configuração de logs
│   ├── 📁 db/                  # Configuração do banco
│   │   ├── base.py             # Base SQLAlchemy
│   │   └── session.py          # Sessões do banco
│   ├── 📁 models/              # Modelos SQLAlchemy
│   │   ├── user.py             # User, Role models
│   │   └── permission.py       # Permission model
│   ├── 📁 schemas/             # Schemas Pydantic
│   │   ├── auth.py             # Schemas de auth
│   │   ├── user.py             # Schemas de usuário
│   │   └── permission.py       # Schemas de permissão
│   ├── 📁 services/            # Lógica de negócio
│   │   ├── auth_service.py     # Serviços de auth
│   │   ├── user_service.py     # Serviços de usuário
│   │   ├── role_service.py     # Serviços de role
│   │   ├── permission_service.py # Serviços de permissão
│   │   └── email_service.py    # Serviços de email
│   ├── 📁 tasks/               # Tarefas Celery
│   │   ├── celery_app.py       # Configuração Celery
│   │   └── tasks.py            # Definição das tasks
│   ├── 📁 templates/           # Templates de email
│   │   └── email/
│   │       └── password_reset.html
│   ├── 📁 tests/               # Testes automatizados
│   │   ├── conftest.py         # Configuração pytest
│   │   ├── test_auth.py        # Testes de auth
│   │   ├── test_users.py       # Testes de usuários
│   │   ├── test_roles.py       # Testes de roles
│   │   └── test_permissions.py # Testes de permissões
│   └── main.py                 # Aplicação FastAPI
├── 📄 docker-compose.yml       # Orquestração Docker
├── 📄 Dockerfile              # Imagem da aplicação
├── 📄 requirements.txt         # Dependências Python
├── 📄 requirements-dev.txt     # Dependências de desenvolvimento
├── 📄 alembic.ini             # Configuração Alembic
├── 📄 .env.example            # Exemplo de variáveis de ambiente
├── 📄 .gitignore              # Arquivos ignorados pelo Git
└── 📄 README.md               # Esta documentação
```

---

## Testes

### **Executando os Testes**

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Executar todos os testes
pytest

# Executar com coverage
pytest --cov=app --cov-report=html

# Executar testes específicos
pytest app/tests/test_auth.py -v

# Executar com logs detalhados
pytest -s -v
```

### **Cobertura de Testes**

O projeto inclui testes para:

- ✅ **Autenticação**: Login, registro, JWT, refresh tokens
- ✅ **Usuários**: CRUD, roles, permissões
- ✅ **Roles**: CRUD, permissões, usuários
- ✅ **Permissões**: CRUD, recursos, ações
- ✅ **Autorização**: RBAC, middlewares
- ✅ **Email**: Templates, envio

### **Configuração de Testes**

Os testes usam um banco PostgreSQL separado configurado no `conftest.py`:

```python
# Database de teste isolada
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"
```

---

## Deploy

### **Docker Compose (Recomendado)**

```bash
# Produção
docker-compose -f docker-compose.yml up -d

# Desenvolvimento
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### **Deploy na Nuvem**

O projeto está pronto para deploy em:

- **AWS**: ECS, EKS, Elastic Beanstalk
- **Google Cloud**: Cloud Run, GKE
- **Azure**: Container Instances, AKS
- **DigitalOcean**: App Platform, Kubernetes
- **Heroku**: Com Heroku Postgres e Redis

### **Configurações de Produção**

```bash
# Variáveis importantes para produção
ENV=production
DEBUG=false
SECRET_KEY=chave_super_segura_gerada_aleatoriamente
CORS_ORIGINS=https://seudominio.com
```

### **Monitoramento**

Health checks disponíveis:

- `GET /health` - Status básico
- `GET /health/detailed` - Status com dependências
- `GET /health/readiness` - Prontidão para receber tráfego
- `GET /health/liveness` - Aplicação está viva

---

## Documentação

### **Documentação Automática**

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### **Recursos Adicionais**

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Pydantic Guide](https://docs.pydantic.dev/)
- [Celery Documentation](https://docs.celeryq.dev/)

---

## Desenvolvimento

### **Setup Local**

```bash
# Clonar e configurar
git clone <repo-url>
cd fastapi-base
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar migrações
alembic upgrade head

# Criar dados iniciais
python -c "import asyncio; from app.scripts.init_data import init_default_data; asyncio.run(init_default_data())"

# Executar servidor
uvicorn app.main:app --reload
```

### **Ferramentas de Desenvolvimento**

```bash
# Formatação de código
black app/
isort app/

# Linting
ruff app/

# Type checking
mypy app/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### **Scripts Úteis**

```bash
# Criar nova migração
alembic revision --autogenerate -m "descrição da mudança"

# Aplicar migrações
alembic upgrade head

# Reverter migração
alembic downgrade -1

# Criar permissões padrão
python -c "import asyncio; from app.scripts.init_data import init_default_data; asyncio.run(init_default_data())"
```

---

## Segurança

### **Recursos de Segurança Implementados**

- ✅ **JWT Tokens** com expiração configurável
- ✅ **Refresh Tokens** para renovação segura
- ✅ **Password Hashing** com BCrypt
- ✅ **CORS** configurável por ambiente
- ✅ **Rate Limiting** preparado
- ✅ **Input Validation** com Pydantic
- ✅ **SQL Injection Protection** via SQLAlchemy ORM
- ✅ **Soft Delete** para auditoria
- ✅ **Middleware de Segurança**

### **Boas Práticas Implementadas**

- Senhas nunca retornadas nas APIs
- Tokens com payload mínimo necessário
- Validação rigorosa de entrada
- Princípio do menor privilégio
- Auditoria completa de ações
- Conexões de banco com pool otimizado

---

## Contribuição

### **Como Contribuir**

1. **Fork** o projeto
2. **Clone** seu fork
3. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
4. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
5. **Push** para a branch (`git push origin feature/AmazingFeature`)
6. **Abra** um Pull Request

### **Diretrizes**

- ✅ Siga os padrões de código estabelecidos
- ✅ Adicione testes para novas funcionalidades
- ✅ Atualize a documentação quando necessário
- ✅ Use commits semânticos
- ✅ Mantenha backward compatibility

### **Reportando Bugs**

Use as [Issues](https://github.com/usuario/fastapi-base/issues) do GitHub com:

- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Ambiente (OS, Python version, etc.)
- Logs relevantes

---

## Roadmap

### **Próximas Funcionalidades**

- [ ] **OAuth2 Social Login** (Google, GitHub, etc.)
- [ ] **Two-Factor Authentication (2FA)**
- [ ] **API Rate Limiting** com Redis
- [ ] **File Upload** com validação
- [ ] **WebSocket Support** para notificações
- [ ] **GraphQL API** alternativa
- [ ] **Multi-tenancy** support
- [ ] **Audit Logs** detalhados
- [ ] **API Versioning** avançado
- [ ] **Background Jobs** dashboard

### **Melhorias Técnicas**

- [ ] **Kubernetes** manifests
- [ ] **Terraform** infrastructure
- [ ] **CI/CD** pipeline completo
- [ ] **Performance** monitoring
- [ ] **Security** scanning automatizado
- [ ] **Documentation** website

---

## Performance

### **Benchmarks**

| Métrica | Valor | Descrição |
|---------|-------|-----------|
| **Startup Time** | ~2s | Tempo de inicialização |
| **Memory Usage** | ~50MB | Uso base de memória |
| **Requests/sec** | ~1000 | Throughput em ambiente padrão |
| **Response Time** | <50ms | Tempo médio de resposta |

### **Otimizações Implementadas**

- **Connection Pooling** para PostgreSQL
- **Lazy Loading** configurado no SQLAlchemy
- **Async/Await** em todas as operações I/O
- **Pydantic** validators otimizados
- **Celery** para tarefas pesadas
- **Redis** cache para sessões

---

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## Autores

- **Desenvolvedor Principal** - [Rafhael H. Cimento](https://github.com/RafhaelH)

---


<div align="center">

**Se este projeto foi útil, considere dar uma estrela! ⭐**

**Tem dúvidas? Abra uma [Issue](https://github.com/RafhaelH/fastapi-base/issues) ou entre em contato!**

---

</div>
