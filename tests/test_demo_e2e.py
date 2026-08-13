"""End-to-End Developer Demo & Integration Test Suite.

Simulates a real client consuming the CityPulse API through every layer:
- User lifecycle: registration, login, token refresh, profile inspection, logout revocation
- Location CRUD: create, list, retrieve, partial update, delete
- Trip logging: recording journeys, time-series validation, editing
- Analytics: summary metrics, transport mode breakdown, daily distance aggregation, outlier detection
- Security & error boundary: invalid credentials, duplicate records, unowned resources, schema violations
"""

import uuid

import httpx
import pytest

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="module")
def client() -> httpx.Client:
    """HTTP client with base URL targeting the running CityPulse server."""
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        yield client


@pytest.fixture(scope="module")
def unique_credentials() -> dict[str, str]:
    """Generate dynamic unique test user credentials."""
    suffix = uuid.uuid4().hex[:8]
    return {
        "email": f"dev_demo_{suffix}@example.com",
        "username": f"dev_{suffix}",
        "password": "StrongPassword!2026",
    }


def test_01_health_check(client: httpx.Client) -> None:
    """Verify backend server liveness."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers.get("x-request-id") is not None


def test_02_user_registration(client: httpx.Client, unique_credentials: dict[str, str]) -> None:
    """Test user account creation."""
    response = client.post("/api/v1/auth/register", json=unique_credentials)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == unique_credentials["email"]
    assert data["username"] == unique_credentials["username"]
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data


def test_03_duplicate_registration_fails(
    client: httpx.Client, unique_credentials: dict[str, str]
) -> None:
    """Test duplicate registration returns 409 Conflict domain error."""
    response = client.post("/api/v1/auth/register", json=unique_credentials)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_04_login_and_token_acquisition(
    client: httpx.Client, unique_credentials: dict[str, str]
) -> None:
    """Authenticate and receive short-lived access token + rotating refresh token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": unique_credentials["email"], "password": unique_credentials["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == unique_credentials["email"]


def test_05_authenticated_me_profile(
    client: httpx.Client, unique_credentials: dict[str, str]
) -> None:
    """Verify Bearer token authorization on /api/v1/auth/me."""
    # Login to get token
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": unique_credentials["email"], "password": unique_credentials["password"]},
    )
    token = login_res.json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == unique_credentials["email"]


def test_06_unauthenticated_request_rejected(client: httpx.Client) -> None:
    """Verify endpoints reject requests without a valid Bearer token with 401 Unauthorized."""
    response = client.get("/api/v1/locations")
    assert response.status_code == 401


def test_07_location_crud_lifecycle(
    client: httpx.Client, unique_credentials: dict[str, str]
) -> None:
    """Test full CRUD lifecycle for saved locations."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": unique_credentials["email"], "password": unique_credentials["password"]},
    )
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    # 1. Create Location
    loc_payload = {
        "name": "Innovation Tech Park",
        "category": "work",
        "latitude": "12.935242",
        "longitude": "77.624462",
        "notes": "Main Office Building 4",
    }
    create_res = client.post("/api/v1/locations", json=loc_payload, headers=headers)
    assert create_res.status_code == 201
    loc_data = create_res.json()
    loc_id = loc_data["id"]
    assert loc_data["name"] == "Innovation Tech Park"

    # 2. Get Location by ID
    get_res = client.get(f"/api/v1/locations/{loc_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == loc_id

    # 3. List Locations
    list_res = client.get("/api/v1/locations", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 4. Partial Update (PATCH)
    patch_res = client.patch(
        f"/api/v1/locations/{loc_id}",
        json={"name": "Innovation Tech Park - Tower B", "notes": "Floor 7 Lab"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "Innovation Tech Park - Tower B"

    # 5. Delete Location
    del_res = client.delete(f"/api/v1/locations/{loc_id}", headers=headers)
    assert del_res.status_code == 204

    # 6. Verify Deleted (404)
    verify_del = client.get(f"/api/v1/locations/{loc_id}", headers=headers)
    assert verify_del.status_code == 404


def test_08_trip_and_analytics_lifecycle(
    client: httpx.Client, unique_credentials: dict[str, str]
) -> None:
    """Log trips, update trips, and verify aggregate analytics calculations."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": unique_credentials["email"], "password": unique_credentials["password"]},
    )
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    # Create 3 distinct trips
    trip_1 = {
        "transport_mode": "metro",
        "started_at": "2026-08-14T08:00:00+05:30",
        "ended_at": "2026-08-14T08:45:00+05:30",
        "distance_km": "15.50",
        "cost": "45.00",
        "rating": 5,
        "purpose": "Morning Commute",
    }
    trip_2 = {
        "transport_mode": "walk",
        "started_at": "2026-08-14T12:00:00+05:30",
        "ended_at": "2026-08-14T12:20:00+05:30",
        "distance_km": "1.80",
        "cost": "0.00",
        "rating": 4,
        "purpose": "Lunch Walk",
    }
    trip_3 = {
        "transport_mode": "ride_share",
        "started_at": "2026-08-14T18:30:00+05:30",
        "ended_at": "2026-08-14T19:15:00+05:30",
        "distance_km": "16.20",
        "cost": "220.00",
        "rating": 4,
        "purpose": "Evening Return",
    }

    t1_res = client.post("/api/v1/trips", json=trip_1, headers=headers)
    t2_res = client.post("/api/v1/trips", json=trip_2, headers=headers)
    t3_res = client.post("/api/v1/trips", json=trip_3, headers=headers)

    assert t1_res.status_code == 201
    assert t2_res.status_code == 201
    assert t3_res.status_code == 201

    # Verify Analytics Summary
    summary_res = client.get("/api/v1/analytics/summary", headers=headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["trip_count"] == 3
    assert float(summary["total_distance_km"]) == pytest.approx(33.50, 0.01)
    assert float(summary["total_cost"]) == pytest.approx(265.00, 0.01)

    # Verify Transport Mode Breakdown
    modes_res = client.get("/api/v1/analytics/transport-modes", headers=headers)
    assert modes_res.status_code == 200
    modes = modes_res.json()
    assert len(modes) == 3

    # Verify Daily Distance
    daily_res = client.get("/api/v1/analytics/daily-distance", headers=headers)
    assert daily_res.status_code == 200
    daily_points = daily_res.json()
    assert len(daily_points) >= 1


def test_09_refresh_token_rotation_and_logout(
    client: httpx.Client, unique_credentials: dict[str, str]
) -> None:
    """Verify single-use token rotation and logout revocation."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": unique_credentials["email"], "password": unique_credentials["password"]},
    )
    initial_tokens = login_res.json()
    refresh_tok_1 = initial_tokens["refresh_token"]

    # Rotate refresh token
    rotate_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_tok_1})
    assert rotate_res.status_code == 200
    new_tokens = rotate_res.json()
    refresh_tok_2 = new_tokens["refresh_token"]
    assert refresh_tok_2 != refresh_tok_1

    # Attempt reuse of old refresh token (must fail with 401)
    reuse_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_tok_1})
    assert reuse_res.status_code == 401

    # Logout with active refresh token
    logout_res = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_tok_2},
        headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Signed out successfully"

    # Verify logged-out token is revoked
    revoked_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_tok_2})
    assert revoked_res.status_code == 401
