"""Fast, database-free coverage of authentication primitives and configuration."""

from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token, decode_token


def test_access_token_cannot_be_used_as_refresh_token() -> None:
    settings = get_settings()
    access_token = create_access_token(user_id="user-1", is_superuser=False, settings=settings)
    try:
        decode_token(token=access_token, expected_type="refresh", settings=settings)
    except Exception as exc:  # TokenError is intentionally an internal security detail.
        assert "token" in str(exc).lower()
    else:
        raise AssertionError("Access token must not validate as a refresh token")


def test_refresh_token_has_unique_identifier_and_expected_claims() -> None:
    settings = get_settings()
    token, token_id, expires_at = create_refresh_token(user_id="user-1", settings=settings)
    claims = decode_token(token=token, expected_type="refresh", settings=settings)

    assert claims["sub"] == "user-1"
    assert claims["jti"] == token_id
    assert expires_at.timestamp() > claims["iat"]
