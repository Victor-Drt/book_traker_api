# 📚 Book Tracker API

API RESTful desenvolvida com Django e Django REST Framework para gerenciar livros, progresso de leitura e estatísticas pessoais. Permite aos usuários cadastrar livros, registrar progresso de leitura, obter recomendações baseadas em categorias e gerar relatórios PDF com histórico completo.

## 🚀 Funcionalidades

- **Gerenciamento de Livros**: CRUD completo para cadastro e gerenciamento de livros pessoais
- **Registro de Progresso**: Sistema para registrar sessões de leitura com data e páginas lidas
- **Cálculo Automático**: Cálculo automático de percentual de conclusão e marcação de livros concluídos
- **Estatísticas**: Visualização de estatísticas de leitura (livros lidos, páginas por semana/mês)
- **Recomendações**: Sistema inteligente de recomendações baseado em categorias mais lidas
- **Relatórios PDF**: Geração assíncrona de relatórios PDF com histórico completo enviados por email
- **Autenticação JWT**: Sistema de autenticação seguro usando JWT (JSON Web Tokens)
- **Documentação Interativa**: API documentada com Swagger UI e ReDoc

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.2.7
- **API**: Django REST Framework 3.16.1
- **Autenticação**: djangorestframework-simplejwt 5.5.1
- **Documentação**: drf-spectacular 0.29.0
- **Banco de Dados**: PostgreSQL (via dj-database-url)
- **Task Queue**: Celery 5.5.3
- **Broker**: Redis 7
- **Geração de PDF**: ReportLab
- **Containerização**: Docker e Docker Compose

## 📋 Pré-requisitos

### Para rodar com Docker (Recomendado):
- Docker Desktop instalado
- Docker Compose instalado (geralmente vem com Docker Desktop)

### Para rodar localmente:
- Python 3.13+
- PostgreSQL 16+
- Redis 7+
- pip (gerenciador de pacotes Python)

## 🔧 Instalação e Configuração

### Opção 1: Usando Docker (Recomendado)

1. **Clone o repositório:**
```bash
git clone https://github.com/Victor-Drt/book_traker_api.git
cd book_traker_api
```

2. **Crie o arquivo `.env` na raiz do projeto:**
```env
# Django
SECRET_KEY=sua-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=*

# Database (será sobrescrito pelo docker-compose, mas necessário para referência)
DATABASE_URL=postgresql://postgres:root@db:5432/book_traker_db

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email (configure conforme necessário)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha
DEFAULT_FROM_EMAIL=seu-email@gmail.com
```

3. **Construa e inicie os containers:**
```bash
docker-compose up --build
```

4. **Crie um superusuário (em outro terminal):**
```bash
docker-compose exec web python manage.py createsuperuser
```

5. **Acesse a API:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- Admin Django: http://localhost:8000/admin/

### Opção 2: Instalação Local

1. **Clone o repositório:**
```bash
git clone https://github.com/Victor-Drt/book_traker_api.git
cd book_traker_api
```

2. **Crie e ative um ambiente virtual:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure o banco de dados PostgreSQL:**
```bash
# Crie o banco de dados
createdb book_traker_db

# Ou via psql
psql -U postgres
CREATE DATABASE book_traker_db;
```

5. **Configure as variáveis de ambiente:**
Crie um arquivo `.env` na raiz do projeto (veja exemplo acima) e ajuste a `DATABASE_URL`:
```env
DATABASE_URL=postgresql://postgres:root@localhost:5432/book_traker_db
```

6. **Execute as migrações:**
```bash
python manage.py migrate
```

7. **Crie um superusuário:**
```bash
python manage.py createsuperuser
```

8. **Inicie o servidor de desenvolvimento:**
```bash
python manage.py runserver
```

9. **Inicie o Celery Worker (em outro terminal):**
```bash
celery -A core.celery_app worker --loglevel=info
```

10. **Inicie o Redis (se necessário):**
```bash
# Windows (com Chocolatey)
choco install redis-64

# Linux
sudo apt-get install redis-server
redis-server

# Mac
brew install redis
brew services start redis
```

## 📡 Endpoints da API

### Autenticação

- `POST /api/token/` - Obter token de acesso (username e password)
- `POST /api/token/refresh/` - Atualizar token de acesso

### Usuários

- `POST /users/` - Criar novo usuário (público)
- `GET /users/{id}/` - Obter detalhes de um usuário (autenticado)

### Livros

- `GET /books/` - Listar todos os livros do usuário autenticado
- `POST /books/` - Criar novo livro
- `GET /books/{id}/` - Obter detalhes de um livro
- `PUT /books/{id}/` - Atualizar livro completo
- `PATCH /books/{id}/` - Atualizar livro parcialmente
- `DELETE /books/{id}/` - Deletar livro
- `POST /books/{id}/progress/` - Registrar progresso de leitura
- `GET /books/{id}/progress/` - Obter informações de progresso
- `GET /books/recommendations/` - Obter recomendações de livros

### Estatísticas

- `GET /stats/` - Obter estatísticas de leitura do usuário

### Exportação

- `POST /export/history/` - Solicitar geração de relatório PDF (enviado por email)

### Documentação

- `GET /api/schema/` - Schema OpenAPI (JSON)
- `GET /api/schema/swagger-ui/` - Documentação Swagger UI
- `GET /api/schema/redoc/` - Documentação ReDoc

## 📁 Estrutura do Projeto

```
book_traker_api/
├── books/                 # App de gerenciamento de livros
│   ├── models.py          # Modelos Books e Progress
│   ├── views.py           # ViewSets e API Views
│   ├── serializers.py     # Serializers para validação
│   ├── services.py        # Lógica de negócio (Services)
│   ├── repository.py      # Acesso a dados (Repository Pattern)
│   └── urls.py            # Rotas da app books
├── users/                 # App de gerenciamento de usuários
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── core/                  # Configurações principais
│   ├── settings.py        # Configurações do Django
│   ├── urls.py            # URLs principais
│   ├── celery_app.py      # Configuração do Celery
│   └── wsgi.py
├── tasks.py               # Tasks assíncronas do Celery
├── manage.py
├── requirements.txt       # Dependências do projeto
├── Dockerfile             # Configuração do container Docker
├── docker-compose.yml     # Orquestração dos serviços
└── .env                   # Variáveis de ambiente (não versionado)
```

## 🔐 Variáveis de Ambiente

O projeto utiliza variáveis de ambiente para configuração. Crie um arquivo `.env` na raiz com as seguintes variáveis:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `SECRET_KEY` | Chave secreta do Django | `django-insecure-...` |
| `DEBUG` | Modo debug | `True` ou `False` |
| `DATABASE_URL` | URL de conexão do PostgreSQL | `postgresql://user:pass@host:port/db` |
| `CELERY_BROKER_URL` | URL do Redis para Celery | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Backend de resultados do Celery | `redis://localhost:6379/0` |
| `EMAIL_BACKEND` | Backend de email | `django.core.mail.backends.console.EmailBackend` |
| `EMAIL_HOST` | Servidor SMTP | `smtp.gmail.com` |
| `EMAIL_PORT` | Porta SMTP | `587` |
| `EMAIL_USE_TLS` | Usar TLS | `True` |
| `EMAIL_HOST_USER` | Usuário do email | `seu-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Senha do email | `sua-senha` |
| `DEFAULT_FROM_EMAIL` | Email remetente padrão | `seu-email@gmail.com` |

## 🧪 Testes

Execute os testes com pytest:

```bash
# Com Docker
docker-compose exec web pytest

# Localmente
pytest
```

## 🐳 Comandos Docker Úteis

```bash
# Iniciar containers
docker-compose up

# Iniciar em background
docker-compose up -d

# Parar containers
docker-compose down

# Ver logs
docker-compose logs -f

# Executar comando no container
docker-compose exec web python manage.py <comando>

# Reconstruir containers
docker-compose up --build

# Acessar shell do container
docker-compose exec web bash
```

## 📖 Documentação da API

A documentação interativa da API está disponível em:

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **Schema OpenAPI**: http://localhost:8000/api/schema/

## 🏗️ Arquitetura

O projeto segue uma arquitetura em camadas:

- **Repository Pattern**: Abstração de acesso a dados
- **Service Layer**: Lógica de negócio isolada
- **ViewSets/APIViews**: Camada de apresentação (API REST)
- **Serializers**: Validação e serialização de dados
- **Tasks (Celery)**: Processamento assíncrono

## 🔄 Fluxo de Uso

1. **Criar usuário**: `POST /users/`
2. **Obter token**: `POST /api/token/` (com username e password)
3. **Cadastrar livros**: `POST /books/` (com token no header)
4. **Registrar progresso**: `POST /books/{id}/progress/`
5. **Ver estatísticas**: `GET /stats/`
6. **Obter recomendações**: `GET /books/recommendations/`
7. **Solicitar relatório**: `POST /export/history/` (receberá por email)

## 📝 Exemplo de Uso

### Criar usuário
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "email": "usuario@example.com",
    "password": "senha123"
  }'
```

### Obter token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "password": "senha123"
  }'
```

### Criar livro (com token)
```bash
curl -X POST http://localhost:8000/books/ \
  -H "Authorization: Bearer <seu-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "O Senhor dos Anéis",
    "author": "J.R.R. Tolkien",
    "category": "Fantasia",
    "total_pages": 1000
  }'
```

## 📄 Licença

Este projeto está sob a licença MIT.

## 👤 Autor

Desenvolvido com ❤️ para gerenciar e acompanhar sua jornada de leitura.

---

**Nota**: Certifique-se de configurar corretamente as variáveis de ambiente, especialmente as credenciais de email para o envio de relatórios PDF.
