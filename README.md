# FastAPI Base

Uma base completa e profissional para projetos FastAPI com sistema de autenticação JWT e RBAC (Role-Based Access Control), projetada para ser escalável, segura e seguir as melhores práticas de desenvolvimento.

## 📋 Características

### Autenticação e Autorização
- **JWT (JSON Web Tokens)** com access e refresh tokens
- **RBAC completo** com usuários, roles e permissões
- Sistema de permissões granulares por recurso e ação
- Middleware de autenticação robusto
- Validação de senhas com critérios de segurança
- Endpoints para alteração de senha e gerenciamento de sessões
- **Reset de senha via email** com tokens seguros
- **Integração Gmail SMTP** para envio de emails

### Gerenciamento de Usuários
- CRUD completo de usuários com paginação e filtros
- Perfis de usuário com campos estendidos (nome, telefone, bio, avatar)
- Sistema de verificação de email
- Controle de status ativo/inativo
- Soft delete para preservar integridade dos dados
- Auditoria completa (created_at, updated_at, last_login)

### Sistema de Roles e Permissões
- Criação e gerenciamento de roles personalizados
- Permissões granulares baseadas em recurso:ação
- Atribuição dinâmica de permissões a roles
- Role padrão para novos usuários
- Sistema de superusuário com acesso total

### Sistema de Emails
- **Gmail SMTP** integrado para envio de emails
- **Templates HTML** responsivos com Jinja2
- **Emails transacionais** (reset de senha, verificação)
- **Fallback texto plano** para compatibilidade
- **Configuração segura** via variáveis de ambiente
- **Logs detalhados** para debugging

### Arquitetura e Padrões
- **Arquitetura em camadas** (Routes → Services → Models)
- **Repository Pattern** implícito nos serviços
- **Dependency Injection** do FastAPI
- **Type Hints** completos em todo o código
- **Async/Await** para operações de I/O
- **Validação robusta** com Pydantic

### Banco de Dados
- **PostgreSQL** como banco principal
- **SQLAlchemy** com suporte async
- **Alembic** para migrações
- **Relacionamentos complexos** bem estruturados
- **Indexação otimizada** para performance

### Docker e Deploy
- **Multi-stage Dockerfile** otimizado
- **Docker Compose** completo com todos os serviços
- **Health checks** em todos os containers
- **Nginx** como proxy reverso
- **Redis** para cache e Celery
- **Profiles** para diferentes ambientes

### Ferramentas de Desenvolvimento
- **Celery** para tarefas assíncronas
- **Redis** para cache e message broker
- **Prometheus + Grafana** para monitoramento
- **Pre-commit hooks** para qualidade de código
- **Ruff** para linting rápido
- **Black + isort** para formatação
- **Pytest** com fixtures avançadas

### Monitoramento e Observabilidade
- Health checks em todos os endpoints críticos
- Logging estruturado com diferentes níveis
- Métricas para Prometheus
- Rate limiting no Nginx
- Headers de segurança configurados

### Testes
- **Cobertura completa** de testes unitários e de integração
- **Fixtures** reutilizáveis para diferentes cenários
- **Testes de autenticação** e autorização
- **Testes de permissões** granulares
- **Mocks** e **factories** para dados de teste

## Início Rápido

### Pré-requisitos
- Docker e Docker Compose
- Python 3.12+ (para desenvolvimento local)
- Make (opcional, para comandos simplificados)

### 1. Clone e Configure

```bash
git clone <seu-repositorio>
cd fastapi-base

# Copie e configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações
```

### 2. Inicie com Docker

```bash
# Inicia todos os serviços
make up

# Ou sem make
docker-compose up -d
```

### 3. Execute as Migrações

```bash
# Via make
make migrate

# Ou diretamente
docker-compose exec api alembic upgrade head
```

### 4. Acesse a Aplicação

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## Comandos Disponíveis

### Docker
```bash
make up              # Inicia serviços em background
make down            # Para todos os serviços
make logs            # Mostra logs
make shell           # Abre shell no container da API
make restart         # Reinicia serviços
```

### Desenvolvimento
```bash
make dev             # Inicia desenvolvimento local
make install-dev     # Instala dependências de desenvolvimento
make quality         # Executa todas as verificações de qualidade
```

### Testes
```bash
make test            # Executa todos os testes
make test-cov        # Executa testes com cobertura
make test-auth       # Testes de autenticação
make test-users      # Testes de usuários
```

### Banco de Dados
```bash
make migrate         # Executa migrações
make reset-db        # Reseta banco (CUIDADO!)
make backup-db       # Faz backup do banco
```

### Qualidade de Código
```bash
make lint            # Verifica código com ruff
make format          # Formata código
make security-check  # Verifica vulnerabilidades
```

## Estrutura do Projeto

```
fastapi-base/
├── app/
│   ├── api/                 # Camada de API
│   │   ├── deps.py         # Dependências de autenticação
│   │   └── routes/         # Endpoints organizados
│   ├── core/               # Configurações centrais
│   │   ├── config.py       # Configurações da aplicação
│   │   ├── security.py     # Utilities de segurança
│   │   └── logging.py      # Configuração de logs
│   ├── db/                 # Camada de banco de dados
│   │   ├── base.py         # Base para modelos
│   │   └── session.py      # Sessões do banco
│   ├── models/             # Modelos SQLAlchemy
│   │   ├── user.py         # Usuários e roles
│   │   └── permission.py   # Permissões
│   ├── schemas/            # Schemas Pydantic
│   │   ├── auth.py         # Schemas de autenticação
│   │   ├── user.py         # Schemas de usuário
│   │   └── permission.py   # Schemas de permissão
│   ├── services/           # Lógica de negócio
│   │   ├── auth_service.py # Serviços de autenticação
│   │   ├── user_service.py # Serviços de usuário
│   │   └── ...
│   ├── tasks/              # Tarefas Celery
│   ├── tests/              # Testes automatizados
│   └── main.py             # Ponto de entrada
├── alembic/                # Migrações do banco
├── scripts/                # Scripts utilitários
├── docker-compose.yml      # Orquestração de containers
├── Dockerfile              # Imagem da aplicação
├── Makefile                # Comandos automatizados
└── requirements.txt        # Dependências
```

## Sistema de Autenticação

### Registro de Usuário
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "first_name": "João",
    "last_name": "Silva"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Uso do Token
```bash
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer <seu-token>"
```

### Reset de Senha
```bash
# Solicitar reset de senha
curl -X POST "http://localhost:8000/api/v1/auth/password-reset" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Confirmar reset com token recebido por email
curl -X POST "http://localhost:8000/api/v1/auth/password-reset/confirm" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "token-recebido-por-email",
    "new_password": "NovaSenha123!"
  }'
```

## Sistema de Permissões

### Estrutura de Permissões
As permissões seguem o padrão `recurso:ação`:

- **users:read** - Visualizar usuários
- **users:write** - Criar/editar usuários
- **users:delete** - Excluir usuários
- **roles:read** - Visualizar roles
- **roles:write** - Criar/editar roles
- **admin:access** - Acesso ao painel admin

### Criando Permissões Personalizadas
```python
# Via API
POST /api/v1/permissions/
{
  "name": "posts:publish",
  "description": "Publicar posts",
  "resource": "posts",
  "action": "publish"
}
```

### Atribuindo Permissões a Roles
```python
# Via API
POST /api/v1/roles/{role_id}/permissions
{
  "permission_ids": [1, 2, 3]
}
```

## Configuração

### Variáveis de Ambiente Principais

```env
# Aplicação
PROJECT_NAME=FastAPI Base
DEBUG=false
ENV=production

# Segurança
SECRET_KEY=seu-secret-key-super-secreto
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Banco de Dados
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
POSTGRES_DB=fastapi_base
POSTGRES_USER=postgres
POSTGRES_PASSWORD=senha-segura

# Redis
REDIS_URL=redis://localhost:6379/0

# Email - Gmail SMTP
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=senha-de-app-do-gmail
EMAIL_FROM=noreply@seuapp.com
EMAIL_FROM_NAME=FastAPI Base
FRONTEND_URL=http://localhost:3000

# CORS
CORS_ORIGINS=https://meuapp.com,https://admin.meuapp.com
```

## Configuração de Email (Gmail)

### 1. Configurar Gmail
1. **Ativar autenticação de 2 fatores** na sua conta Google
2. **Gerar senha de app:**
   - Acesse [Google Account](https://myaccount.google.com)
   - Segurança → Senhas de app
   - Selecione "Email" → Gerar senha
   - Use esta senha no `SMTP_PASSWORD`

### 2. Configurar Variáveis
```env
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app-gerada  # NÃO use sua senha normal!
EMAIL_FROM=noreply@seuapp.com          # Email que aparece como remetente
EMAIL_FROM_NAME=Seu App                # Nome que aparece como remetente
FRONTEND_URL=https://seuapp.com        # URL do frontend para links
```

### 3. Testar Email
```bash
# Testar reset de senha
curl -X POST "http://localhost:8000/api/v1/auth/password-reset" \
  -H "Content-Type: application/json" \
  -d '{"email": "seu-email@teste.com"}'
```

### 📧 **Templates de Email**
Os templates HTML estão em `app/templates/email/`:
- **password_reset.html** - Email de reset de senha
- Personalize conforme sua marca/design

## Deploy com Docker

### Desenvolvimento
```bash
docker-compose up -d
```

### Produção com Nginx
```bash
docker-compose --profile production up -d
```

### Com Monitoramento
```bash
docker-compose --profile monitoring up -d
```

Isso iniciará:
- **API** na porta 8000
- **PostgreSQL** na porta 5432
- **Redis** na porta 6379
- **Nginx** nas portas 80/443 (produção)
- **Prometheus** na porta 9090 (monitoramento)
- **Grafana** na porta 3000 (monitoramento)

## Executando Testes

### Todos os Testes
```bash
make test
```

### Testes com Cobertura
```bash
make test-cov
```

### Testes Específicos
```bash
make test-auth       # Apenas autenticação
make test-users      # Apenas usuários
make test-roles      # Apenas roles
```

### Testes Manuais
```bash
# Health check
curl http://localhost:8000/health

# Documentação
curl http://localhost:8000/api/v1/docs
```

## Monitoramento

### Health Checks
- **API**: `GET /health`
- **Database**: Verificação automática de conexão
- **Redis**: Verificação automática de conexão

### Métricas (Prometheus)
- Tempo de resposta das APIs
- Número de requests por endpoint
- Status dos health checks
- Métricas de sistema

### Logs
Os logs são estruturados e incluem:
- Request ID para rastreamento
- Tempo de resposta
- Erros detalhados
- Ações de autenticação/autorização

## Segurança

### Implementações de Segurança
- **JWT** com expiração configurável
- **Refresh tokens** para renovação segura
- **Rate limiting** no Nginx
- **Headers de segurança** (CORS, CSP, etc.)
- **Validação rigorosa** de entrada
- **Proteção contra SQL injection**
- **Passwords hasheadas** com bcrypt
- **Usuário não-root** nos containers

### Rate Limiting
- **API geral**: 10 requests/segundo
- **Login**: 5 requests/minuto
- **Configurável** no nginx.conf

## Expandindo o Projeto

### Adicionando Novos Endpoints
1. Crie o schema em `app/schemas/`
2. Crie o modelo em `app/models/`
3. Crie o serviço em `app/services/`
4. Crie as rotas em `app/api/routes/`
5. Adicione testes em `app/tests/`

### Adicionando Novas Permissões
1. Use a API para criar: `POST /api/v1/permissions/`
2. Ou use o script: `make create-default-permissions`

### Personalizando para Seu Projeto
1. Modifique as configurações em `app/core/config.py`
2. Atualize os modelos conforme sua necessidade
3. Personalize os schemas de validação
4. Ajuste as permissões padrão
5. Configure as variáveis de ambiente

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Execute os testes: `make test`
5. Execute o linting: `make quality`
6. Abra um Pull Request

### Padrões de Código
- **Docstrings** em português para descrições
- **Código, variáveis e funções** em inglês
- **Type hints** obrigatórios
- **Testes** para toda nova funcionalidade
- **Commits** descritivos em inglês

## Suporte

- **Issues**: Reporte bugs e solicite features
- **Documentação**: Disponível em `/docs` quando rodando
- **Email**: [rafhaelh33@gmail.com]

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

## Roadmap

### Próximas Funcionalidades
- [ ] Sistema de notificações
- [ ] Upload de arquivos com S3
- [ ] Sistema de auditoria completo
- [ ] Integração com OAuth2 (Google, GitHub)
- [ ] Cache avançado com Redis
- [ ] Webhook system
- [ ] API versioning
- [ ] Rate limiting por usuário
- [ ] Sistema de quotas
- [ ] Verificação de email por token
- [ ] Templates de email avançados

### Melhorias Planejadas
- [ ] Testes de performance
- [ ] Documentação em vídeo
- [ ] CI/CD pipelines
- [ ] Deployment automatizado
- [ ] Métricas de negócio
- [ ] Dashboard administrativo

---

**Desenvolvido usando FastAPI e as melhores práticas de desenvolvimento Python.**
