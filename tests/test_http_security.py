"""HTTP-layer protections that are testable without MySQL."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_response_has_baseline_security_headers() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["x-request-id"]


def test_invalid_password_is_not_echoed_in_validation_errors() -> None:
    client = TestClient(app)
    supplied_password = "not-a-strong-password"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "person@example.com", "username": "person", "password": supplied_password},
    )

    assert response.status_code == 422
    assert supplied_password not in response.text
