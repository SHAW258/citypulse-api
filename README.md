<div align="center">

# 🏙️ CityPulse — Privacy-Conscious Mobility & Urban Analytics

[![Python](https://img.shields.io/badge/Python-3.14%20%7C%203.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-0.40+-499848?style=flat&logo=gunicorn&logoColor=white)](https://www.uvicorn.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![asyncmy](https://img.shields.io/badge/asyncmy-0.2.10+-005C84?style=flat)](https://github.com/long2ice/asyncmy)
[![MySQL](https://img.shields.io/badge/MySQL-8.4%20LTS-4479A1?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose%20v2-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2.12+-E92063?style=flat&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![PyJWT](https://img.shields.io/badge/PyJWT-2.11+-000000?style=flat&logo=jsonwebtokens&logoColor=white)](https://pyjwt.readthedocs.io/)
[![Argon2](https://img.shields.io/badge/Argon2id-pwdlib-8A2BE2?style=flat)](https://github.com/frankie567/pwdlib)
[![Pytest](https://img.shields.io/badge/Pytest-9.0+-0A9EDC?style=flat&logo=pytest&logoColor=white)](https://pytest.org/)
[![Ruff](https://img.shields.io/badge/Ruff-0.14+-D7FF64?style=flat&logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-red?style=flat)](LICENSE)

*An enterprise-grade, privacy-conscious mobility and urban analytics backend with Argon2id authentication, rotating JWT tokens, spatio-temporal location tracking, and statistical outlier detection.*

<br/>

[Architecture](#-system-architecture-diagram) • [Database Schema](#-database-schema--er-diagram) • [Getting Started](#-quick-start--setup) • [API Reference](#-api-endpoints-overview) • [Detailed Setup Guide](SETUP.md) • [Tech Stack](#-technology-stack)

</div>

---

## 📑 Table of Contents

- [Technology Stack](#-technology-stack)
- [System Architecture Diagram](#-system-architecture-diagram)
- [Database Schema & ER Diagram](#-database-schema--er-diagram)
- [Quick Start & Setup](#-quick-start--setup)
- [API Endpoints Overview](#-api-endpoints-overview)
- [Security Model & Baseline](#-security-model--baseline)
- [Project Directory Structure](#-project-directory-structure)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Detailed Setup Guide](SETUP.md)

---

## 🚀 Technology Stack

| Layer / Concern | Technology | Version / Spec | Purpose & Justification |
|---|---|---|---|
| **Web Framework** | [FastAPI](https://fastapi.tiangolo.com/) | `>=0.128` | High-performance async REST API with automatic OpenAPI documentation and dependency injection. |
| **ASGI Server** | [Uvicorn](https://www.uvicorn.org/) | `>=0.40` | Lightning-fast async server with standard protocol support and live-reload worker management. |
| **ORM & Persistence** | [SQLAlchemy](https://www.sqlalchemy.org/) | `>=2.0.46` | Modern async 2.0 syntax with mapped columns, strong typing, and relationship cascading. |
| **Async DB Driver** | [asyncmy](https://github.com/long2ice/asyncmy) | `>=0.2.10` | High-throughput asynchronous driver for MySQL using asyncio and Cython extensions. |
| **Database** | [MySQL](https://www.mysql.com/) | `8.4 LTS` | Relational storage engine with native JSON, transactional guarantees, and strict constraints. |
| **Schema Migrations**| [Alembic](https://alembic.sqlalchemy.org/) | `>=1.18` | Version-controlled, idempotent database schema migrations with async context support. |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) | `v2+` / `pydantic-settings` | Strict schema validation, environment configuration parsing, and input sanitization. |
| **Authentication** | [PyJWT](https://pyjwt.readthedocs.io/) | `>=2.11` | Cryptographic JWT token encoding, verification, and rotation. |
| **Password Hashing** | [pwdlib](https://github.com/frankie567/pwdlib) | `[argon2] >=0.3` | State-of-the-art Argon2id cryptographic hashing to resist GPU/ASIC attacks. |
| **Testing** | [pytest](https://pytest.org/) & [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) | `>=9.0` / `>=1.3` | Async unit, security, and integration test suite with fixture scopes. |
| **Code Quality** | [Ruff](https://docs.astral.sh/ruff/) | `>=0.14` | High-speed linter and formatter enforcing modern Python idioms. |

---

## 🏛 System Architecture Diagram

The CityPulse API follows a strict separation of concerns with unidirectional dependency flow:

```mermaid
flowchart TD
    Client["Client / Frontend App (Web / Mobile / CLI)"]
    
    subgraph FastAPI_Application["FastAPI Application (ASGI / Uvicorn)"]
        subgraph Middleware_Pipeline["Security & Transport Middleware"]
            TrustedHost["TrustedHostMiddleware (Host Header Whitelist)"]
            HTTPSRedirect["HTTPSRedirectMiddleware (SSL Enforcer)"]
            CORSMiddleware["CORSMiddleware (Strict Origin Whitelist)"]
            SecurityMiddleware["RequestSecurityMiddleware (Rate Limiting, Size Checks, Headers)"]
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
            AuthService["AuthService (Password hashing, JWT issuing/rotating)"]
            LocationService["LocationService (Ownership enforcement, Geo validation)"]
            TripService["TripService (Metrics computation, Trip validation)"]
            AnalyticsService["AnalyticsService (Aggregations, Outlier detection)"]
        end
        
        subgraph Repository_Layer["Data Access Repositories"]
            UserRepo["UserRepository"]
            LocationRepo["LocationRepository"]
            TripRepo["TripRepository"]
        end
        
        subgraph ORM_Engine["SQLAlchemy 2.0 Async Engine"]
            AsyncEngine["AsyncEngine / Connection Pool"]
            AsyncMyDriver["asyncmy Cython Driver"]
        end
    end
    
    subgraph Persistence["Database Storage Layer"]
        MySQL[("MySQL 8.4 Database")]
    end

    Client -->|HTTP Request| TrustedHost
    TrustedHost --> HTTPSRedirect
    HTTPSRedirect --> CORSMiddleware
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
    AsyncEngine --> AsyncMyDriver
    AsyncMyDriver -->|Port 3306| MySQL
```

---

## 📊 Database Schema & ER Diagram

CityPulse models data around user ownership, privacy isolation, revocable tokens, saved locations, and recorded mobility trips.

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

## ⚡ Quick Start & Setup

> 💡 *For a detailed installation walkthrough, prerequisites, and troubleshooting guide, please see [SETUP.md](SETUP.md).*

### 1. Set Up Environment & Install Dependencies

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # On Linux/macOS: source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Configure environment file
Copy-Item .env.example .env     # On Linux/macOS: cp .env.example .env
```

### 2. Start MySQL (Docker)

```powershell
docker compose up -d mysql
```

### 3. Run Migrations & Start Server

```powershell
# Apply Alembic database migrations
alembic upgrade head

# Start Uvicorn development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Access Interactive Documentation

Open [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs) in your browser.

---

## 📡 API Endpoints Overview

All v1 routes are mounted under `/api/v1`:

| Domain | Method | Endpoint | Description | Auth Required |
|---|---|---|---|:---:|
| **Health** | `GET` | `/health` | Server liveness check | No |
| **Auth** | `POST` | `/api/v1/auth/register` | Register a new user account | No |
| **Auth** | `POST` | `/api/v1/auth/login` | Authenticate with credentials (issues access + refresh tokens) | No |
| **Auth** | `POST` | `/api/v1/auth/refresh` | Rotate refresh token & issue new access token | No |
| **Auth** | `POST` | `/api/v1/auth/logout` | Revoke active refresh token | Yes |
| **Auth** | `GET` | `/api/v1/auth/me` | Retrieve profile of authenticated user | Yes |
| **Locations** | `POST` | `/api/v1/locations/` | Create a new user location | Yes |
| **Locations** | `GET` | `/api/v1/locations/` | List all locations for authenticated user | Yes |
| **Locations** | `GET` | `/api/v1/locations/{id}` | Get details of a specific location | Yes |
| **Locations** | `PATCH` | `/api/v1/locations/{id}` | Update an existing location | Yes |
| **Locations** | `DELETE` | `/api/v1/locations/{id}` | Delete a location | Yes |
| **Trips** | `POST` | `/api/v1/trips/` | Log a new mobility journey / trip | Yes |
| **Trips** | `GET` | `/api/v1/trips/` | List user trips with pagination & filters | Yes |
| **Trips** | `GET` | `/api/v1/trips/{id}` | Get details of a single trip | Yes |
| **Trips** | `PATCH` | `/api/v1/trips/{id}` | Update trip attributes | Yes |
| **Trips** | `DELETE` | `/api/v1/trips/{id}` | Delete a trip record | Yes |
| **Analytics** | `GET` | `/api/v1/analytics/summary` | Aggregate metrics (total trips, distance, cost, duration) | Yes |
| **Analytics** | `GET` | `/api/v1/analytics/transport-modes` | Breakdown by transportation mode | Yes |
| **Analytics** | `GET` | `/api/v1/analytics/daily-distance` | Daily mobility distance time-series | Yes |
| **Analytics** | `GET` | `/api/v1/analytics/outliers` | Statistical speed and distance outlier detection | Yes |

---

## 🔒 Security Model & Baseline

- **Argon2id Password Hashing**: State-of-the-art password hashing using `pwdlib[argon2]`.
- **Rotating Refresh Tokens**: Refresh tokens are stored by unique token ID, rotated on every refresh, and revoked on logout.
- **Reuse Detection**: Automatic revocation and reuse protection for refresh tokens.
- **Strict Data Isolation**: Multi-tenant data segregation where every query is strictly constrained to the authenticated user (`user_id`).
- **Defensive HTTP Headers**: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy.
- **Per-IP Rate Throttling**: Sliding window rate limiting middleware to prevent brute force and DDoS attacks.
- **Strict CORS & Host Whitelist**: Whitelist-based origin and host validation.

---

## 📁 Project Directory Structure

```text
backend/
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
├── .env                          # Local environment secrets (ignored by git)
├── .env.example                  # Environment configuration template
├── alembic.ini                   # Alembic configuration
├── docker-compose.yml            # Local MySQL 8.4 Docker service
├── pyproject.toml                # Project metadata & tool configuration
├── requirements.txt              # Production and development dependencies
├── SETUP.md                      # Comprehensive setup & installation guide
└── README.md                     # Project documentation overview
```

---

## 🧪 Testing & Quality Assurance

```powershell
# Run the complete test suite
pytest

# Run tests with verbose output
pytest -v

# Run code linter
ruff check .

# Format code
ruff format .
```

---

## 📄 License & Proprietary Notice

Copyright © 2026 SHAW258. All rights reserved.

This project and its source code are **Proprietary and Confidential**. Public viewing of this repository is permitted solely for demonstration, inspection, and portfolio evaluation. Unauthorized copying, cloning for derivation, distribution, reproduction, or commercial deployment without prior written permission from the copyright holder is strictly prohibited. See the [LICENSE](LICENSE) file for complete terms.

