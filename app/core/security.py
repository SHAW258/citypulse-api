"""Password and JWT security primitives."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import Settings

password_hasher = PasswordHash.recommended()


class TokenError(Exception):
    """Raised when a supplied JSON Web Token is invalid for this operation."""


def hash_password(password: str) -> str:
    """Hash a password using the recommended Argon2id configuration."""

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Constant-time verify a password against its stored Argon2id hash."""

    return password_hasher.verify(password, password_hash)


def verify_and_update_password(password: str, password_hash: str) -> tuple[bool, str | None]:
    """Verify password and return updated hash if rehashing is recommended."""

    return password_hasher.verify_and_update(password, password_hash)


def _issue_token(
    *,
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    settings: Settings,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, str, datetime]:
    now = datetime.now(UTC)
    expires_at = now + expires_delta
    token_id = str(uuid4())
    payload: dict[str, Any] = {
        "sub": subject,
        "jti": token_id,
        "type": token_type,
        "iat": now,
        "nbf": now,
        "exp": expires_at,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    if extra_claims:
        payload.update(extra_claims)
    encoded = jwt.encode(
        payload,
        settings.secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    return encoded, token_id, expires_at


def create_access_token(*, user_id: str, is_superuser: bool, settings: Settings) -> str:
    """Issue a short-lived access token for authenticated API calls."""

    token, _, _ = _issue_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        settings=settings,
        extra_claims={"admin": is_superuser},
    )
    return token


def create_refresh_token(*, user_id: str, settings: Settings) -> tuple[str, str, datetime]:
    """Issue a refresh token and return its signed value, identifier, and expiration."""

    return _issue_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        settings=settings,
    )


def decode_token(*, token: str, expected_type: str, settings: Settings) -> dict[str, Any]:
    """Validate signature, registered claims, and intended token type."""

    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
            options={"require": ["exp", "iat", "nbf", "sub", "jti", "type"]},
        )
    except InvalidTokenError as exc:
        raise TokenError("Invalid or expired token") from exc

    if payload.get("type") != expected_type:
        raise TokenError("Unexpected token type")
    if not isinstance(payload.get("sub"), str) or not isinstance(payload.get("jti"), str):
        raise TokenError("Malformed token claims")
    return payload

