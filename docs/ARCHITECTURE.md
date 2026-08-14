# 🏛 System Architecture & Design

This document details the architectural topology, design patterns, and layer responsibilities of the **CityPulse API**.

---

## 🏗 High-Level Architecture Flowchart

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

## 🧩 Architectural Principles & Patterns

### 1. Clean Layered Architecture
- **Routers (`app/api/v1/`)**: Pure HTTP transport layer. Validates inputs via Pydantic DTOs and handles HTTP status codes.
- **Dependency Injection (`app/api/deps.py`)**: Resolves authentication, token decoding, database async sessions, and service instances.
- **Service Layer (`app/services/`)**: Enforces business domain logic, password verification, token rotation compromise detection, and statistical outlier math.
- **Repository Layer (`app/repositories/`)**: Abstracted data access with SQLAlchemy 2.0 async queries.
- **Models (`app/models/`)**: Declarative database schema definitions with strict constraints.

### 2. Dual-Engine Async Database Support
- **PostgreSQL / Supabase**: High-performance async operations via `asyncpg`.
- **MySQL 8.4 LTS**: Supported via `asyncmy` driver.
- **UTC Datetime Serialization**: Cross-dialect `UTCDateTime` type ensuring timezone consistency across engines.

### 3. Defense-in-Depth Security
- **Argon2id Cryptographic Hashing**: Memory-hard password hashing.
- **Single-Use JWT Refresh Tokens**: Automatic user session revocation if token reuse is detected.
- **Sliding-Window IP Rate Limiter**: Middleware-level traffic throttling.
- **Security Headers**: HSTS, CSP, X-Content-Type-Options (`nosniff`), X-Frame-Options (`DENY`).

### 4. Synchronous WSGI Adapter (`SyncASGIMiddleware`)
- Located in [`wsgi.py`](../wsgi.py), allowing deployment on standard single-threaded WSGI hosts without Gunicorn/Uvicorn ASGI prerequisites.

---

[⬅ Back to Main README](../README.md) • [Next: Database Schema ➡](DATABASE_SCHEMA.md)
