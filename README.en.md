<div align="center">

# FastAPI Starter

**Production-ready FastAPI project template** — Integrated logging, database, JWT auth, Docker, and CI/CD. Start building your backend in minutes.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI/CD](https://github.com/yourname/fastapi-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/yourname/fastapi-starter/actions)

**English** | [中文](README.md)

</div>

---

## Features

- **FastAPI** — High-performance async web framework with auto-generated interactive API docs
- **JWT Authentication** — Built-in register, login, token refresh, and role-based access (user/admin)
- **Database** — SQLAlchemy 2.0 ORM with MySQL / PostgreSQL / SQLite support out of the box
- **Unified Logging** — Console + file dual output with auto-rotation and structured formatting
- **Global Exception Handling** — Business exceptions, validation errors, and HTTP errors all return standardized JSON
- **Docker** — Multi-stage build, docker-compose one-click startup (includes MySQL)
- **CI/CD** — GitHub Actions for automated linting + multi-version testing + Docker build
- **Full Test Suite** — pytest integration tests with isolated in-memory database
- **Clean Architecture** — Layered design (router / service / model / schema), easy to extend

---

## Quick Start

### Option 1: Local Development

```bash
# 1. Clone the repository
git clone https://github.com/yourname/fastapi-starter.git
cd fastapi-starter

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your database URL and JWT secret

# 5. Start the server
python -m app.main
```

Once running, visit:
- API Docs (Swagger): http://localhost:8000/docs
- API Docs (ReDoc): http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Option 2: Docker (Recommended for Deployment)

```bash
git clone https://github.com/yourname/fastapi-starter.git
cd fastapi-starter

# One-click startup (builds image + starts MySQL + starts app)
docker-compose up -d

# View logs
docker-compose logs -f web
```

---

## API Examples

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "email": "demo@example.com",
    "password": "demo123456",
    "full_name": "Demo User"
  }'
```

### 2. Login and Get Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=demo&password=demo123456"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Access Protected Endpoint

```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Project Structure

```
fastapi-starter/
├── app/
│   ├── __init__.py
│   ├── main.py              # App entry point, FastAPI instance
│   ├── config.py            # Config management (pydantic-settings)
│   ├── database.py          # DB connection and session
│   ├── dependencies.py      # Global dependencies (current user, admin)
│   ├── models/              # SQLAlchemy models
│   │   └── user.py
│   ├── schemas/             # Pydantic request/response models
│   │   └── user.py
│   ├── routers/             # API route layer
│   │   ├── auth.py          # Auth routes (register/login/refresh)
│   │   └── user.py          # User management routes
│   ├── services/            # Business logic layer
│   │   └── auth.py
│   └── utils/               # Utility modules
│       ├── logger.py        # Logging configuration
│       ├── exceptions.py    # Custom exceptions and handlers
│       └── security.py      # Password hashing, JWT tokens
├── tests/
│   └── test_main.py         # Integration tests
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI/CD
├── .env.example             # Environment variables template
├── .gitignore
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # App + MySQL orchestration
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project metadata and pytest config
├── README.md                # Chinese documentation
└── README.en.md             # English documentation
```

---

## Common Commands

```bash
# Run tests
pytest tests/ -v

# Code formatting (Black)
black app/ tests/

# Linting (Ruff)
ruff check app/ tests/

# Docker
docker-compose up -d          # Start
docker-compose down           # Stop
docker-compose logs -f web    # View app logs
docker-compose restart web    # Restart app
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | FastAPI Starter | Application name |
| `APP_ENV` | development | Runtime environment (development/production) |
| `APP_DEBUG` | true | Debug mode |
| `DATABASE_URL` | sqlite:///./test.db | Database connection string |
| `JWT_SECRET_KEY` | change-me | JWT signing secret (**must change in production**) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Access token expiry (minutes) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Refresh token expiry (days) |
| `LOG_LEVEL` | INFO | Log level |
| `CORS_ORIGINS` | localhost:3000,5173 | Allowed CORS origins |

---

## Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

If this project helped you, please give it a Star!

</div>
