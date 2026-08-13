"""Request-validation tests that do not require a database server."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest
from app.schemas.location import LocationCreate
from app.schemas.trip import TripCreate


def test_registration_requires_a_strong_password() -> None:
    with pytest.raises(ValidationError):
        RegisterRequest(email="person@example.com", username="person", password="onlylowercase123")


def test_location_coordinates_must_be_paired() -> None:
    with pytest.raises(ValidationError):
        LocationCreate(name="Home", latitude=12.97)


def test_trip_requires_timezone_aware_and_ordered_timestamps() -> None:
    with pytest.raises(ValidationError):
        TripCreate(
            transport_mode="metro",
            started_at=datetime(2026, 8, 14, 10, 0),
            ended_at=datetime(2026, 8, 14, 9, 0),
            distance_km="4.2",
        )
