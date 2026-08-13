"""Location request and response schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field, model_validator

from app.models.location import LocationCategory
from app.schemas.base import ResponseSchema, StrictSchema


class LocationCreate(StrictSchema):
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Display name for the location (e.g. Home, Office)",
    )
    category: LocationCategory = Field(
        default=LocationCategory.OTHER, description="Location category"
    )
    latitude: Decimal | None = Field(
        default=None, ge=-90, le=90, decimal_places=6, description="WGS84 Latitude"
    )
    longitude: Decimal | None = Field(
        default=None, ge=-180, le=180, decimal_places=6, description="WGS84 Longitude"
    )
    notes: str | None = Field(
        default=None, max_length=2_000, description="Optional private notes about the place"
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Central Residence",
                    "category": "home",
                    "latitude": "12.971598",
                    "longitude": "77.594562",
                    "notes": "Primary apartment building near the metro station",
                }
            ]
        },
    )

    @model_validator(mode="after")
    def coordinates_are_paired(self) -> LocationCreate:
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be supplied together")
        return self


class LocationUpdate(StrictSchema):
    name: str | None = Field(
        default=None, min_length=1, max_length=100, description="Updated display name"
    )
    category: LocationCategory | None = Field(default=None, description="Updated location category")
    latitude: Decimal | None = Field(
        default=None, ge=-90, le=90, decimal_places=6, description="Updated Latitude"
    )
    longitude: Decimal | None = Field(
        default=None, ge=-180, le=180, decimal_places=6, description="Updated Longitude"
    )
    notes: str | None = Field(default=None, max_length=2_000, description="Updated notes")

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Tech Hub HQ",
                    "category": "work",
                    "latitude": "12.935242",
                    "longitude": "77.624462",
                    "notes": "4th floor workspace",
                }
            ]
        },
    )


class LocationResponse(ResponseSchema):
    id: str = Field(description="Unique location UUID")
    name: str = Field(description="Location name")
    category: LocationCategory = Field(description="Location category")
    latitude: Decimal | None = Field(default=None, description="Latitude coordinate")
    longitude: Decimal | None = Field(default=None, description="Longitude coordinate")
    notes: str | None = Field(default=None, description="Private notes")
    created_at: datetime = Field(description="Creation timestamp (UTC)")
    updated_at: datetime = Field(description="Last updated timestamp (UTC)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "name": "Central Residence",
                    "category": "home",
                    "latitude": "12.971598",
                    "longitude": "77.594562",
                    "notes": "Primary apartment building near the metro station",
                    "created_at": "2026-08-14T08:00:00Z",
                    "updated_at": "2026-08-14T08:00:00Z",
                }
            ]
        },
    )
