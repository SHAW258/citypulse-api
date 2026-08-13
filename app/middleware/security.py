"""Security headers and lightweight request-level protections."""

from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import Settings
from app.middleware.rate_limit import client_ip, general_rate_limiter


class RequestSecurityMiddleware(BaseHTTPMiddleware):
    """Apply correlation IDs, request limits, headers, and coarse IP throttling."""

    def __init__(self, app, settings: Settings) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                exceeds_limit = int(content_length) > self.settings.max_request_size_bytes
            except ValueError:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid Content-Length"},
                )
            if exceeds_limit:
                return Response(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        try:
            await general_rate_limiter.enforce(
                f"api:{client_ip(request)}",
                limit=self.settings.general_rate_limit_per_minute,
            )
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
                headers=exc.headers,
            )
        request_id = request.headers.get("x-request-id")
        if request_id is None or len(request_id) > 100:
            request_id = str(uuid4())

        response = await call_next(request)
        response.headers.setdefault("X-Request-ID", request_id)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=()",
        )
        is_docs_route = (
            request.url.path.endswith("/docs")
            or request.url.path.endswith("/openapi.json")
            or request.url.path.endswith("/redoc")
        )
        if is_docs_route:
            response.headers.setdefault(
                "Content-Security-Policy",
                "default-src 'self' https://cdn.jsdelivr.net; "
                "connect-src 'self' http://localhost:* http://127.0.0.1:* http://10.0.2.2:* ws:; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "frame-ancestors 'none'; base-uri 'self'",
            )
        else:
            response.headers.setdefault(
                "Content-Security-Policy",
                "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
            )
        if self.settings.force_https:
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response
