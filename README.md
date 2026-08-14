# 🏙️ CityPulse API

[![Render Live](https://img.shields.io/badge/Render-Live%20Production-24c8db?style=flat&logo=render&logoColor=white)](https://citypulse-api-tjpr.onrender.com/api/v1/docs)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat&logo=supabase&logoColor=white)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=flat)](LICENSE)

An enterprise-grade, privacy-conscious mobility and urban analytics backend featuring Argon2id authentication, rotating single-use JWTs, spatio-temporal journey tracking, and statistical outlier anomaly detection.

---

## 🌐 Live Service & Interactive Docs

- **Interactive Swagger UI**: [https://citypulse-api-tjpr.onrender.com/api/v1/docs](https://citypulse-api-tjpr.onrender.com/api/v1/docs)
- **Health Check Probe**: `GET` [https://citypulse-api-tjpr.onrender.com/health](https://citypulse-api-tjpr.onrender.com/health)
- **Pre-Seeded Demo Accounts**: [👉 View Credentials](docs/DEMO_ACCOUNTS.md)

---

## ⚡ Quick Start

```powershell
.\.venv\Scripts\Activate.ps1
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
*Access local Swagger explorer at:* [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)

---

## 📚 Documentation Index

| Domain | Guide | Description |
| :--- | :--- | :--- |
| 📱 **Frontend & Mobile** | [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) | Complete React, Next.js, React Native, & Flutter integration |
| 📦 **Module Deep Dives** | [docs/modules/README.md](docs/modules/README.md) | Full-stack guides for [Auth](docs/modules/AUTH_MODULE.md), [Trips](docs/modules/TRIPS_MODULE.md), [Locations](docs/modules/LOCATIONS_MODULE.md), [Analytics](docs/modules/ANALYTICS_MODULE.md) |
| 🏛 **Architecture** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System topology, layer responsibilities, & WSGI adapter |
| 📊 **Database Schema** | [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | Mermaid ER diagram, schema tables, constraints, & indexes |
| 📡 **API Reference** | [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | Complete HTTP route catalog & permissions |
| 🚀 **Deployment** | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Render, Supabase, Docker, & WSGI deployment |
| 📁 **Codebase Structure** | [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Directory layout & file responsibilities |
| 🛠 **Local Onboarding** | [SETUP.md](SETUP.md) | Developer environment setup & prerequisites |

---

## 📄 License
Copyright © 2026 SHAW258. All rights reserved. Proprietary and confidential. See [LICENSE](LICENSE).
