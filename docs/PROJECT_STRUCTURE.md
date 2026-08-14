# 📁 Repository & Codebase Directory Structure

This document outlines the directory structure, file responsibilities, and architectural layers of the **CityPulse API**.

---

## 🌳 Directory Tree

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
├── docs/                         # Modular Documentation Chunks
│   ├── modules/                  # Full-stack module deep-dives (Auth, Trips, etc.)
│   ├── ARCHITECTURE.md           # System architecture & design patterns
│   ├── DATABASE_SCHEMA.md        # Database schema, ER diagram, & dictionary
│   ├── API_REFERENCE.md          # Comprehensive endpoint catalog
│   ├── DEPLOYMENT.md             # Cloud deployment (Render, Supabase, Docker)
│   └── PROJECT_STRUCTURE.md      # Codebase directory layout
├── tests/                        # Automated Pytest suite
│   ├── test_demo_e2e.py          # End-to-End integration test suite
│   ├── test_http_security.py     # Middleware & security header tests
│   ├── test_schemas.py           # Validation schema tests
│   └── test_security.py          # Password & JWT crypto tests
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git exclusions
├── alembic.ini                   # Alembic configuration
├── Dockerfile                    # Containerization definition
├── docker-compose.yml            # Local MySQL 8.4 Docker service
├── FRONTEND_INTEGRATION.md       # Frontend & Mobile integration guide
├── LICENSE                       # Proprietary copyright notice
├── pyproject.toml                # Project metadata & tool configuration
├── render.yaml                   # Infrastructure-as-code for Render
├── requirements.txt              # Production and development dependencies
├── SETUP.md                      # Detailed developer onboarding guide
├── wsgi.py                       # Synchronous WSGI adapter for standard web hosts
└── README.md                     # Main project landing page & overview
```

---

[⬅ Back to Main README](../README.md)
