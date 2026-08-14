# 📡 API Endpoints Reference

Complete catalog of all HTTP routes exposed by the **CityPulse API (v1)**.

---

## 🌐 Base URLs & Interactive Documentation

- **Live Production (Render)**: `https://citypulse-api-tjpr.onrender.com`
- **Interactive Swagger UI**: [https://citypulse-api-tjpr.onrender.com/api/v1/docs](https://citypulse-api-tjpr.onrender.com/api/v1/docs)
- **OpenAPI 3.1 JSON Schema**: `https://citypulse-api-tjpr.onrender.com/api/v1/openapi.json`

---

## 📋 Comprehensive Endpoint Catalog

| Domain | Method | Route | Description | Auth Required |
| :--- | :---: | :--- | :--- | :---: |
| **System** | `GET` | `/health` | Application liveness probe | ❌ No |
| **System** | `GET` | `/api/v1/docs` | Interactive Swagger UI Explorer | ❌ No |
| **System** | `GET` | `/api/v1/openapi.json` | OpenAPI 3.1 JSON Schema specification | ❌ No |
| **Auth** | `POST` | `/api/v1/auth/register` | Register new user account | ❌ No |
| **Auth** | `POST` | `/api/v1/auth/login` | Authenticate credentials; issues token pair | ❌ No |
| **Auth** | `POST` | `/api/v1/auth/refresh` | Rotate single-use refresh token | ❌ No |
| **Auth** | `POST` | `/api/v1/auth/logout` | Revoke active refresh token session | ✅ Bearer |
| **Auth** | `POST` | `/api/v1/auth/revoke-all` | Revoke all active sessions across all devices | ✅ Bearer |
| **Auth** | `GET` | `/api/v1/auth/me` | Retrieve authenticated user profile | ✅ Bearer |
| **Locations** | `POST` | `/api/v1/locations` | Create a new user-saved location | ✅ Bearer |
| **Locations** | `GET` | `/api/v1/locations` | List all saved locations with pagination | ✅ Bearer |
| **Locations** | `GET` | `/api/v1/locations/{id}` | Retrieve details of a specific location | ✅ Bearer |
| **Locations** | `PATCH` | `/api/v1/locations/{id}` | Update existing saved location | ✅ Bearer |
| **Locations** | `DELETE` | `/api/v1/locations/{id}` | Delete a saved location | ✅ Bearer |
| **Trips** | `POST` | `/api/v1/trips` | Record a new mobility journey | ✅ Bearer |
| **Trips** | `GET` | `/api/v1/trips` | List trips with pagination, filters, & sorting | ✅ Bearer |
| **Trips** | `GET` | `/api/v1/trips/{id}` | Retrieve details of a single trip | ✅ Bearer |
| **Trips** | `PATCH` | `/api/v1/trips/{id}` | Update trip attributes | ✅ Bearer |
| **Trips** | `DELETE` | `/api/v1/trips/{id}` | Delete a logged trip | ✅ Bearer |
| **Analytics** | `GET` | `/api/v1/analytics/summary` | Aggregate KPIs (distance, cost, time, count) | ✅ Bearer |
| **Analytics** | `GET` | `/api/v1/analytics/by-mode` | Modal split breakdown by transport mode | ✅ Bearer |
| **Analytics** | `GET` | `/api/v1/analytics/daily-distance`| Daily distance time-series aggregation | ✅ Bearer |
| **Analytics** | `GET` | `/api/v1/analytics/outliers` | Statistical speed and distance anomaly detection | ✅ Bearer |

---

## 📦 Granular Module Deep-Dives

For complete request/response JSON payloads, TypeScript interfaces, and React/Vue/Mobile integration examples:

- 🔐 **[Authentication Module Guide](modules/AUTH_MODULE.md)**
- 🚗 **[Trips & Journeys Module Guide](modules/TRIPS_MODULE.md)**
- 📍 **[Locations & Places Module Guide](modules/LOCATIONS_MODULE.md)**
- 📊 **[Analytics & Outliers Module Guide](modules/ANALYTICS_MODULE.md)**
- 🌐 **[Full-Stack Module Master Index](modules/README.md)**

---

[⬅ Back to Main README](../README.md) • [Next: Deployment Guide ➡](DEPLOYMENT.md)
