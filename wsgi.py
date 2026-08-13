"""WSGI entrypoint for PythonAnywhere and WSGI application servers."""

from __future__ import annotations

from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from project root
env_file = Path(__file__).resolve().parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file, override=True)

import asyncio
import http
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv

# Explicitly load .env from project root
env_file = Path(__file__).resolve().parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file, override=True)

from app.main import app


class SyncASGIMiddleware:
    """Synchronous WSGI adapter for running ASGI apps under single-threaded WSGI (uWSGI)."""

    def __init__(self, asgi_app: Any) -> None:
        self.asgi_app = asgi_app

    def __call__(
        self,
        environ: dict[str, Any],
        start_response: Callable[..., Any],
    ) -> list[bytes]:
        headers: list[tuple[bytes, bytes]] = []
        for k, v in environ.items():
            if k.startswith("HTTP_"):
                header_name = k[5:].lower().replace("_", "-").encode("latin-1")
                headers.append((header_name, str(v).encode("latin-1")))
        if "CONTENT_TYPE" in environ:
            headers.append((b"content-type", str(environ["CONTENT_TYPE"]).encode("latin-1")))
        if "CONTENT_LENGTH" in environ and environ["CONTENT_LENGTH"]:
            headers.append((b"content-length", str(environ["CONTENT_LENGTH"]).encode("latin-1")))

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": environ.get("SERVER_PROTOCOL", "HTTP/1.1").split("/")[-1],
            "method": environ.get("REQUEST_METHOD", "GET"),
            "scheme": environ.get("wsgi.url_scheme", "http"),
            "path": environ.get("PATH_INFO", ""),
            "raw_path": environ.get("PATH_INFO", "").encode("ascii"),
            "query_string": environ.get("QUERY_STRING", "").encode("ascii"),
            "root_path": environ.get("SCRIPT_NAME", ""),
            "headers": headers,
            "server": (
                environ.get("SERVER_NAME", "localhost"),
                int(environ.get("SERVER_PORT", 80)),
            ),
        }

        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0) or 0)
        except (TypeError, ValueError):
            content_length = 0

        body = environ["wsgi.input"].read(content_length) if content_length > 0 else b""

        status_code = 200
        resp_headers: list[tuple[str, str]] = []
        resp_body: list[bytes] = []

        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message: dict[str, Any]) -> None:
            nonlocal status_code, resp_headers, resp_body
            if message["type"] == "http.response.start":
                status_code = message["status"]
                resp_headers = [
                    (k.decode("latin-1"), v.decode("latin-1"))
                    for k, v in message.get("headers", [])
                ]
            elif message["type"] == "http.response.body":
                resp_body.append(message.get("body", b""))

        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.asgi_app(scope, receive, send))
        finally:
            loop.close()

        try:
            status_phrase = http.HTTPStatus(status_code).phrase
        except ValueError:
            status_phrase = "Unknown"

        start_response(f"{status_code} {status_phrase}", resp_headers)
        return resp_body


# PythonAnywhere looks for the 'application' callable
application = SyncASGIMiddleware(app)
