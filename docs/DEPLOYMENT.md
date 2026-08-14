# 🚀 Cloud Deployment & Production Guide

This guide covers deployment procedures for Render, Supabase, Docker, and standard WSGI/uWSGI web hosting environments.

---

## 🌐 1. Deploying to Render (Recommended)

Render is the primary cloud host for CityPulse API.

### Steps:
1. Connect repository [`SHAW258/citypulse-api`](https://github.com/SHAW258/citypulse-api) on **[Render Dashboard](https://dashboard.render.com)**.
2. Select **Web Service** with **Python 3.12+** runtime.
3. Configure Build & Start commands:
   - **Build Command**:
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
4. Configure Environment Variables in the Render Settings:
   - `DATABASE_URL`: `postgresql+asyncpg://postgres.[PROJECT]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres`
   - `SECRET_KEY`: `[YOUR_CRYPTOGRAPHIC_SECRET_KEY_MIN_32_CHARS]`
   - `ENVIRONMENT`: `production`
   - `DEBUG`: `false`

---

## 🐘 2. Supabase PostgreSQL Configuration

1. Create a project at [Supabase](https://supabase.com/).
2. Under **Project Settings $\rightarrow$ Database**, copy the **Transaction Connection Pooler** string (Port `5432` or `6543`).
3. Replace the driver prefix with `postgresql+asyncpg://` in your `DATABASE_URL`.
4. Apply migrations:
   ```bash
   alembic upgrade head
   ```

---

## 🐳 3. Docker Container Deployment

Use the multi-stage [`Dockerfile`](../Dockerfile):

```bash
# Build the container image
docker build -t citypulse-api:latest .

# Run container exposing port 8000
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" \
  -e SECRET_KEY="your-production-secret-key" \
  --name citypulse citypulse-api:latest
```

---

## ⚙️ 4. Synchronous WSGI Server Adapter

For hosting platforms without native ASGI/Uvicorn support (such as standard cPanel, Apache mod_wsgi, or classic WSGI servers), CityPulse includes a zero-dependency synchronous runner in [`wsgi.py`](../wsgi.py):

```bash
# Standard WSGI command
gunicorn wsgi:application --workers 4 --bind 0.0.0.0:8000
```

---

[⬅ Back to Main README](../README.md) • [Next: Project Structure ➡](PROJECT_STRUCTURE.md)
