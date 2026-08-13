"""Small dependency-free in-memory rate limiter for a single API process."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque

from fastapi import HTTPException, status
from starlette.requests import Request


class SlidingWindowRateLimiter:
    """Bound requests per key in a rolling one-minute window.

    Replace this with a shared Redis limiter when running multiple API replicas.
    """

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def enforce(self, key: str, *, limit: int) -> None:
        now = time.monotonic()
        window_start = now - 60
        async with self._lock:
            events = self._events[key]
            while events and events[0] <= window_start:
                events.popleft()
            if len(events) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again shortly.",
                    headers={"Retry-After": "60"},
                )
            events.append(now)


general_rate_limiter = SlidingWindowRateLimiter()
login_rate_limiter = SlidingWindowRateLimiter()


def client_ip(request: Request) -> str:
    """Use the direct peer only; forwarded headers require explicit proxy configuration."""

    return request.client.host if request.client else "unknown"
