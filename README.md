<div align="center">

# 🏙️ CityPulse — Privacy-Conscious Mobility & Urban Analytics API

[![Render Live](https://img.shields.io/badge/Render-Live%20Production-24c8db?style=for-the-badge&logo=render&logoColor=white)](https://citypulse-api-tjpr.onrender.com/api/v1/docs)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.12%20%7C%203.14-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%20Async-D71F00?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL%20(Live)-3ECF8E?style=flat&logo=supabase&logoColor=white)](https://supabase.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.4%20LTS-4479A1?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Argon2](https://img.shields.io/badge/Argon2id-Cryptographic%20Hashing-8A2BE2?style=flat)](https://github.com/frankie567/pwdlib)
[![Pytest](https://img.shields.io/badge/Pytest-100%25%20Passing-0A9EDC?style=flat&logo=pytest&logoColor=white)](https://pytest.org/)
[![Ruff](https://img.shields.io/badge/Ruff-0.14+-D7FF64?style=flat&logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-red?style=flat)](LICENSE)

*An enterprise-grade, privacy-conscious mobility and urban analytics backend with Argon2id cryptographic authentication, rotating single-use JWT tokens, spatio-temporal journey tracking, and statistical outlier detection.*

<br/>

[Live API Docs (Render)](#-live-deployments--interactive-docs) • [Frontend & Mobile Guide](FRONTEND_INTEGRATION.md) • [Pre-Seeded Accounts](#-pre-seeded-demo-credentials) • [Architecture](#-system-architecture) • [Database Schema](#-database-schema--er-diagram) • [API Endpoints](#-api-endpoints-reference) • [Setup Guide](#-local-quick-start) • [Deployment](#-cloud-deployment-guide)

</div>

---

## 🌐 Live Deployments & Interactive Docs

| Deployment Platform | Status | Interactive Swagger Docs | Health Probe | OpenAPI Spec |
| :--- | :---: | :--- | :--- | :--- |
| **Render Production (Supabase)** | 🟢 **Live** | **[Live Swagger UI](https://citypulse-api-tjpr.onrender.com/api/v1/docs)** | `GET` **[/health](https://citypulse-api-tjpr.onrender.com/health)** | **[/openapi.json](https://citypulse-api-tjpr.onrender.com/api/v1/openapi.json)** |
| **PythonAnywhere WebApp** | 🟢 **Live** | **[PythonAnywhere UI](https://indrada.pythonanywhere.com/api/v1/docs)** | `GET` **[/health](https://indrada.pythonanywhere.com/health)** | **[/openapi.json](https://indrada.pythonanywhere.com/api/v1/openapi.json)** |

---

## 🔑 Pre-Seeded Demo Credentials

The live production Supabase database comes pre-seeded with **160+ realistic mobility journeys, saved locations, and user accounts**:

| Account Name | Email / Username | Password | Seeded Data Volume |
| :--- | :--- | :--- | :--- |
| **Alice Urban (Primary)** | `alice_urban@example.com` | `StrongPassword!2026` | 26 Trips, 7 Saved Locations |
| **Bob Commuter** | `bob_commuter@example.com` | `StrongPassword!2026` | 28 Trips, 6 Saved Locations |
| **Carol Cyclist** | `carol_cyclist@example.com` | `StrongPassword!2026` | 24 Trips, 5 Saved Locations |
| **David Transit** | `david_transit@example.com` | `StrongPassword!2026` | 26 Trips, 6 Saved Locations |
| **Eva Walker** | `eva_walker@example.com` | `StrongPassword!2026` | 26 Trips, 7 Saved Locations |

---

## 🚀 Key Features & Highlights

- **Dual-Engine Async Persistence**: Seamless cross-dialect support for **PostgreSQL (Supabase via `asyncpg`)** and **MySQL 8.4 LTS (via `asyncmy`)** with UTC-aware datetime serialization.
- **Enterprise Authentication**: State-of-the-art **Argon2id password hashing** paired with **rotating single-use JWT refresh tokens** featuring automated token-reuse compromise detection.
- **Privacy-First Data Segregation**: Strict multi-tenant isolation where all queries, mutations, and analytics are bounded to the authenticated `user_id`.
- **Advanced Mobility Analytics**: Aggregated journey analytics, transportation mode breakdowns (Walk, Bike, Bus, Train, Metro, Car, Auto, Ride Share), time-series daily distance, and interquartile statistical speed/distance anomaly detection.
- **Defense-in-Depth Middleware**: Sliding-window IP rate limiting, strict CORS configuration, TrustedHost verification, and hardened security headers (`Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy`).
- **Synchronous WSGI Adapter (`SyncASGIMiddleware`)**: High-performance synchronous runner in [`wsgi.py`](wsgi.py) enabling zero-dependency deployment under standard single-threaded WSGI servers like PythonAnywhere uWSGI.

---

## 🏛 System Architecture

```mermaid
flowchart TD
    Client["Client App (Web / Mobile / CLI / Postman)"]
    
    subgraph FastAPI_Application["FastAPI Application Layer (ASGI / Uvicorn / WSGI)"]
        subgraph Middleware_Pipeline["Security & Transport Pipeline"]
            TrustedHost["TrustedHostMiddleware (Host Header Whitelist)"]
            CORSMiddleware["CORSMiddleware (Strict Origin Whitelist)"]
            SecurityMiddleware["RequestSecurityMiddleware (Rate Limiting, Payload Guards, Security Headers)"]
        end
        
        subgraph API_Routers["API Router Layer (/api/v1)"]
            AuthRouter["Auth Router (/auth)"]
            LocationRouter["Locations Router (/locations)"]
            TripRouter["Trips Router (/trips)"]
            AnalyticsRouter["Analytics Router (/analytics)"]
        end
        
        subgraph DI_Layer["FastAPI Dependency Injection"]
            DBSession["get_db_session() (AsyncSession)"]
            CurrentUser["get_current_active_user() (JWT Verification)"]
            ServiceProviders["Service Dependency Injectors"]
        end
        
        subgraph Service_Layer["Business Logic Services"]
            AuthService["AuthService (Argon2id hashing, JWT rotation)"]
            LocationService["LocationService (Ownership enforcement, Geo validation)"]
            TripService["TripService (Metrics computation, Trip validation)"]
            AnalyticsService["AnalyticsService (Aggregations, Outlier math)"]
        end
        
        subgraph Repository_Layer["Data Access Layer (Repository Pattern)"]
            UserRepo["UserRepository"]
            LocationRepo["LocationRepository"]
            TripRepo["TripRepository"]
        end
        
        subgraph ORM_Engine["SQLAlchemy 2.0 Async Engine"]
            AsyncEngine["AsyncEngine / Connection Pool"]
            AsyncPgDriver["asyncpg (PostgreSQL)"]
            AsyncMyDriver["asyncmy (MySQL)"]
        end
    end
    
    subgraph Persistence["Cloud & Local Database Storage"]
        Supabase[("Supabase PostgreSQL (Cloud)")]
        MySQL[("MySQL 8.4 (Local / Container)")]
    end

    Client -->|HTTPS Request| TrustedHost
    TrustedHost --> CORSMiddleware
    CORSMiddleware --> SecurityMiddleware
    SecurityMiddleware --> API_Routers
    
    AuthRouter --> DI_Layer
    LocationRouter --> DI_Layer
    TripRouter --> DI_Layer
    AnalyticsRouter --> DI_Layer
    
    DI_Layer --> Service_Layer
    
    AuthService --> UserRepo
    LocationService --> LocationRepo
    TripService --> TripRepo
    TripService --> LocationRepo
    AnalyticsService --> TripRepo
    
    UserRepo --> DBSession
    LocationRepo --> DBSession
    TripRepo --> DBSession
    
    DBSession --> AsyncEngine
    AsyncEngine --> AsyncPgDriver
    AsyncEngine --> AsyncMyDriver
    AsyncPgDriver -->|Port 5432 / 6543| Supabase
    AsyncMyDriver -->|Port 3306| MySQL
```

---

## 📊 Database Schema & ER Diagram

```mermaid
erDiagram
    users ||--o{ refresh_tokens : "owns / rotates"
    users ||--o{ locations : "owns"
    users ||--o{ trips : "logs"
    locations ||--o{ trips : "origin of"
    locations ||--o{ trips : "destination of"

    users {
        string id PK "UUID String(36)"
        string email UK "String(320), Indexed"
        string username UK "String(32), Indexed"
        string password_hash "String(255) (Argon2id)"
        boolean is_active "Boolean (Default: true)"
        boolean is_superuser "Boolean (Default: false)"
        datetime last_login_at "UTC DateTime (Nullable)"
        datetime created_at "UTC DateTime"
        datetime updated_at "UTC DateTime"
    }

    refresh_tokens {
        string id PK "UUID String(36)"
        string token_id UK "UUID String(36), Indexed"
        string user_id FK "UUID String(36) -> users.id (CASCADE)"
        datetime expires_at "UTC DateTime"
        datetime created_at "UTC DateTime"
        datetime revoked_at "UTC DateTime (Nullable)"
        string client_ip "String(45) (Nullable)"
        string user_agent "String(512) (Nullable)"
    }

    locations {
        string id PK "UUID String(36)"
        string user_id FK "UUID String(36) -> users.id (CASCADE)"
        string name "String(100)"
        string category "Enum (HOME, WORK, COLLEGE, FOOD, LEISURE, SHOPPING, HEALTH, OTHER)"
        decimal latitude "DECIMAL(8, 6) (Nullable)"
        decimal longitude "DECIMAL(9, 6) (Nullable)"
        text notes "Text (Nullable)"
        datetime created_at "UTC DateTime"
        datetime updated_at "UTC DateTime"
    }

    trips {
        string id PK "UUID String(36)"
        string user_id FK "UUID String(36) -> users.id (CASCADE)"
        string origin_location_id FK "UUID String(36) -> locations.id (SET NULL, Nullable)"
        string destination_location_id FK "UUID String(36) -> locations.id (SET NULL, Nullable)"
        string transport_mode "Enum (WALK, BIKE, BUS, TRAIN, METRO, CAR, AUTO, RIDE_SHARE, OTHER)"
        datetime started_at "UTC DateTime"
        datetime ended_at "UTC DateTime"
        decimal distance_km "DECIMAL(8, 2) (Check >= 0)"
        decimal cost "DECIMAL(10, 2) (Check >= 0, Default: 0)"
        integer rating "Integer (Check 1..5, Nullable)"
        string purpose "String(100) (Nullable)"
        text notes "Text (Nullable)"
        datetime created_at "UTC DateTime"
        datetime updated_at "UTC DateTime"
    }
```

---

## 📡 API Endpoints Reference

All Version 1 routes are mounted under `/api/v1`:

| Domain | Method | Endpoint | Description | Auth Required |
| :--- | :---: | :--- | :--- | :---: |
| **System** | `GET` | `/health` | Application liveness probe | No |
| **System** | `GET` | `/api/v1/docs` | Interactive Swagger UI Explorer | No |
| **System** | `GET` | `/api/v1/openapi.json` | OpenAPI 3.1 JSON Schema specification | No |
| **Auth** | `POST` | `/api/v1/auth/register` | Register new user account with unique email and username | No |
| **Auth** | `POST` | `/api/v1/auth/login` | Authenticate credentials; issues JWT access + refresh tokens | No |
| **Auth** | `POST` | `/api/v1/auth/refresh` | Rotate single-use refresh token & issue fresh access token | No |
| **Auth** | `POST` | `/api/v1/auth/logout` | Revoke active refresh token session | Yes |
| **Auth** | `GET` | `/api/v1/auth/me` | Retrieve authenticated user profile | Yes |
| **Locations** | `POST` | `/api/v1/locations/` | Create a new user-saved location | Yes |
| **Locations** | `GET` | `/api/v1/locations/` | List all saved locations for authenticated user | Yes |
| **Locations** | `GET` | `/api/v1/locations/{id}` | Retrieve details of a specific saved location | Yes |
| **Locations** | `PATCH` | `/api/v1/locations/{id}` | Update existing saved location attributes | Yes |
| **Locations** | `DELETE` | `/api/v1/locations/{id}` | Delete a saved location | Yes |
| **Trips** | `POST` | `/api/v1/trips/` | Record a new mobility journey | Yes |
| **Trips** | `GET` | `/api/v1/trips/` | List trips with pagination, date filtering, and sorting | Yes |
| **Trips** | `GET` | `/api/v1/trips/{id}` | Retrieve details of a single trip | Yes |
| **Trips** | `PATCH` | `/api/v1/trips/{id}` | Update trip attributes | Yes |
| **Trips** | `DELETE` | `/api/v1/trips/{id}` | Delete a logged trip | Yes |
| **Analytics** | `GET` | `/api/v1/analytics/summary` | Aggregate summary (total trips, distance, cost, time) | Yes |
| **Analytics** | `GET` | `/api/v1/analytics/transport-modes` | Modal split analysis with trip counts and distances | Yes |
| **Analytics** | `GET` | `/api/v1/analytics/daily-distance` | Daily mobility distance time-series aggregation | Yes |
| **Analytics** | `GET` | `/api/v1/analytics/outliers` | Statistical speed and distance outlier detection | Yes |

---

## ⚡ Local Quick Start

### 1. Clone & Initialize Virtual Environment

```bash
git clone https://github.com/SHAW258/citypulse-api.git
cd citypulse-api

# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example configuration
cp .env.example .env
```

Edit `.env` to configure your database connection:
```env
# For Supabase (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres

# For Local MySQL
# MYSQL_HOST=localhost
# MYSQL_PORT=3306
# MYSQL_DATABASE=citypulse
# MYSQL_USERNAME=citypulse_user
# MYSQL_PASSWORD=citypulse_pass

SECRET_KEY=your-secure-random-secret-key-at-least-32-chars
ENVIRONMENT=development
DEBUG=true
```

### 3. Run Migrations & Start Server

```bash
# Run database schema migrations
alembic upgrade head

# Start development ASGI server with live-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs) in your browser.

---

## 🧪 Testing & Code Quality

```bash
# Run the automated pytest test suite
pytest

# Run tests with verbose output
pytest -v

# Run code linter
ruff check .

# Auto-format codebase
ruff format .
```

---

## 🚀 Cloud Deployment Guide

### A. Deploy to Render (Recommended)

1. Connect your repository [`SHAW258/citypulse-api`](https://github.com/SHAW258/citypulse-api) on **[Render Dashboard](https://dashboard.render.com)**.
2. Select **Web Service** with **Python 3.12** runtime.
3. Configure Build & Start commands:
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variables:
   - `DATABASE_URL`: `postgresql+asyncpg://postgres.[PROJECT]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres`
   - `SECRET_KEY`: `[YOUR_SECRET_KEY]`
   - `ENVIRONMENT`: `production`
   - `DEBUG`: `false`

### B. Deploy to PythonAnywhere

1. Upload repository files into `/home/<username>/citypulse-api`.
2. Create Python 3.10 virtualenv: `mkvirtualenv --python=python3.10 citypulse-venv && pip install -r requirements.txt`.
3. In PythonAnywhere **Web** tab, configure WSGI configuration file:
   ```python
   import sys, os
   path = '/home/<username>/citypulse-api'
   if path not in sys.path:
       sys.path.insert(0, path)
   os.chdir(path)
   from wsgi import application
   ```
4. Reload the web app.

---

## 📁 Repository Structure

```text
citypulse-api/
├── alembic/                      # Database migrations
│   ├── versions/                 # Revision scripts
│   └── env.py                    # Async migration runtime environment
├── app/
│   ├── api/                      # HTTP Routers & Dependency Injection
│   │   ├── deps.py               # Authentication & DB session dependencies
│   │   └── v1/                   # Version 1 API route endpoints
│   ├── core/                     # Core configs, security & exceptions
│   │   ├── config.py             # Pydantic Settings & environment loader
│   │   ├── exceptions.py         # Domain error hierarchy
│   │   └── security.py           # Password hashing & JWT token generators
│   ├── db/                       # Database setup & types
│   │   ├── base.py               # Declarative SQLAlchemy base
│   │   ├── session.py            # Async engine & sessionmaker
│   │   └── types.py              # UTC DateTime cross-dialect handler
│   ├── middleware/               # HTTP security, rate limiting & headers
│   │   └── security.py           # RequestSecurityMiddleware
│   ├── models/                   # SQLAlchemy ORM database models
│   │   ├── location.py           # Location entity
│   │   ├── mixins.py             # UUID and timestamp reusable mixins
│   │   ├── refresh_token.py      # RefreshToken entity
│   │   ├── trip.py               # Trip entity
│   │   └── user.py               # User entity
│   ├── repositories/             # Data Access Layer (Clean Architecture)
│   │   ├── location.py           # Location queries & persistence
│   │   ├── trip.py               # Trip queries & aggregations
│   │   └── user.py               # User & token persistence
│   ├── schemas/                  # Pydantic Request & Response DTOs
│   │   ├── analytics.py          # Analytics response schemas
│   │   ├── auth.py               # Registration, Login, Token schemas
│   │   ├── location.py           # Location CRUD schemas
│   │   └── trip.py               # Trip CRUD schemas
│   ├── services/                 # Business Logic Layer
│   │   ├── analytics.py          # Mobility analytics & outlier math
│   │   ├── auth.py               # User registration & token lifecycle
│   │   ├── location.py           # Location validation & operations
│   │   └── trip.py               # Trip calculation & CRUD operations
│   └── main.py                   # FastAPI application factory & middleware setup
├── tests/                        # Automated Pytest suite
│   ├── test_http_security.py     # Middleware & security header tests
│   ├── test_schemas.py           # Validation schema tests
│   └── test_security.py          # Password & JWT crypto tests
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git exclusions
├── alembic.ini                   # Alembic configuration
├── Dockerfile                    # Containerization definition
├── docker-compose.yml            # Local MySQL 8.4 Docker service
├── LICENSE                       # Proprietary copyright notice
├── pyproject.toml                # Project metadata & tool configuration
├── render.yaml                   # Infrastructure-as-code for Render
├── requirements.txt              # Production and development dependencies
├── SETUP.md                      # Detailed developer onboarding guide
├── wsgi.py                       # Synchronous WSGI adapter for standard web hosts
└── README.md                     # Comprehensive project documentation
```

---

## 📄 License & Proprietary Notice

Copyright © 2026 SHAW258. All rights reserved.

This project and its source code are **Proprietary and Confidential**. Public viewing of this repository is permitted solely for demonstration, inspection, and portfolio evaluation. Unauthorized copying, cloning for derivation, distribution, reproduction, or commercial deployment without prior written permission from the copyright holder is strictly prohibited. See the [LICENSE](LICENSE) file for complete terms.
