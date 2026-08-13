# CityPulse API — Setup & Installation Guide

This guide provides step-by-step instructions to set up, configure, migrate, test, and run the **CityPulse API** locally or in a containerized environment.

---

## 1. Prerequisites

Ensure you have the following installed on your machine:

- **Python**: Version `3.12+` (tested with Python `3.14`)
- **Docker & Docker Compose**: Recommended for local MySQL (e.g., Docker Desktop) OR a running **MySQL 8.0+ / 8.4+** instance
- **Git** (for version control)
- **PowerShell** (Windows) or **Bash** (macOS/Linux)

---

## 2. Clone & Environment Setup

### 2.1 Clone Repository
```powershell
git clone <repository-url>
cd backend
```

### 2.2 Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS (Bash):**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2.3 Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Environment Configuration

Copy the sample environment file to `.env`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Linux / macOS (Bash):**
```bash
cp .env.example .env
```

### Key Environment Variables (`.env`)

| Variable | Default Value | Description |
|---|---|---|
| `ENVIRONMENT` | `development` | Environment mode (`development`, `staging`, `production`) |
| `DEBUG` | `true` | Enables FastAPI debug mode & detailed error traces |
| `APP_NAME` | `CityPulse API` | Application title for OpenAPI / Swagger |
| `API_V1_PREFIX` | `/api/v1` | Base URL prefix for all version 1 routes |
| `MYSQL_HOST` | `localhost` | MySQL hostname or Docker container host |
| `MYSQL_PORT` | `3306` | MySQL port |
| `MYSQL_DATABASE` | `citypulse` | Target database name |
| `MYSQL_USERNAME` | `root` | Database username |
| `MYSQL_PASSWORD` | `root` | Database password |
| `SECRET_KEY` | *(generate a 32+ char secret)* | Secret key for signing JWT tokens |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | JWT Access Token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token validity window |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins (JSON array) |
| `ALLOWED_HOSTS` | `["localhost","127.0.0.1"]` | Allowed HTTP Host headers |
| `FORCE_HTTPS` | `false` | Enable HTTPS redirection (set `true` in production) |

---

## 4. Start Database (MySQL)

### Using Docker Compose (Recommended)
Start the preconfigured MySQL 8.4 container in background:
```powershell
docker compose up -d mysql
```

Check container status and logs:
```powershell
docker compose ps
docker compose logs mysql
```

### Using Native / External MySQL
If using an existing local MySQL installation, ensure the service is running on port `3306` and create the database if not already present:
```sql
CREATE DATABASE IF NOT EXISTS citypulse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 5. Database Migrations (Alembic)

Apply all database migrations to create the required schema tables, indexes, and constraints:

```powershell
alembic upgrade head
```

### Helpful Alembic Commands

- **Check current revision**:
  ```powershell
  alembic current
  ```
- **View migration history**:
  ```powershell
  alembic history --verbose
  ```
- **Create a new migration after model changes**:
  ```powershell
  alembic revision --autogenerate -m "describe_changes"
  ```
- **Rollback previous migration**:
  ```powershell
  alembic downgrade -1
  ```

---

## 6. Run Application Server

### Development Mode (with Live Reload)
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Production Mode (Multi-worker ASGI)
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 7. Verify API & Documentation

Once the server is running, visit:

- **Swagger UI (Interactive Docs)**: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)
- **OpenAPI Schema (JSON)**: [http://127.0.0.1:8000/api/v1/openapi.json](http://127.0.0.1:8000/api/v1/openapi.json)
- **Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 8. Testing & Code Quality

### Run Test Suite
Run unit, integration, and security tests with `pytest`:
```powershell
pytest
```

Run tests with verbose output and coverage:
```powershell
pytest -v
```

### Linting & Formatting
Run `ruff` for ultra-fast Python linting and code formatting checks:
```powershell
# Check for lint issues
ruff check .

# Fix auto-fixable lint issues
ruff check --fix .

# Check formatting
ruff format --check .

# Auto-format codebase
ruff format .
```

---

## 9. Troubleshooting & FAQ

### 1. `OperationalError: (1049, "Unknown database 'citypulse'")`
- **Cause**: MySQL is running but the database `citypulse` does not exist yet.
- **Fix**: Run the following quick command or execute `CREATE DATABASE citypulse;` in your MySQL client:
  ```powershell
  python -c "import asyncio, asyncmy; async def init(): conn = await asyncmy.connect(host='localhost', port=3306, user='root', password='root'); cur = conn.cursor(); await cur.execute('CREATE DATABASE IF NOT EXISTS citypulse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'); await conn.commit(); await conn.ensure_closed(); asyncio.run(init())"
  alembic upgrade head
  ```

### 2. `ConnectionRefusedError` or Port 3306 unreachable
- **Cause**: MySQL container or service is not running.
- **Fix**: Verify docker container state with `docker compose ps` or start it via `docker compose up -d mysql`.

### 3. `StarletteDeprecationWarning` in Pytest
- **Cause**: Deprecation notice from Starlette's TestClient integration.
- **Fix**: This does not affect test execution and is safely handled in current configurations.
