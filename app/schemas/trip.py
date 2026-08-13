"""Trip request and response schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.models.trip import TransportMode
from app.schemas.base import ResponseSchema, StrictSchema


class TripCreate(StrictSchema):
    origin_location_id: str | None = Field(
        default=None,
        min_length=36,
        max_length=36,
        description="Optional origin location UUID",
    )
    destination_location_id: str | None = Field(
        default=None,
        min_length=36,
        max_length=36,
        description="Optional destination location UUID",
    )
    transport_mode: TransportMode = Field(
        description="Mode of transit used (e.g. walk, bike, bus, train, metro, car, auto, ride_share)"
    )
    started_at: datetime = Field(description="Trip start timestamp with timezone (ISO 8601)")
    ended_at: datetime = Field(description="Trip arrival timestamp with timezone (ISO 8601)")
    distance_km: Decimal = Field(
        ge=0,
        le=50_000,
        max_digits=8,
        decimal_places=2,
        description="Distance traveled in kilometers",
    )
    cost: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        le=1_000_000,
        max_digits=10,
        decimal_places=2,
        description="Monetary expense for the trip",
    )
    rating: int | None = Field(
        default=None, ge=1, le=5, description="Personal trip satisfaction rating (1 to 5)"
    )
    purpose: str | None = Field(
        default=None, max_length=100, description="Brief reason/purpose for the journey"
    )
    notes: str | None = Field(
        default=None, max_length=2_000, description="Optional private trip journal or remarks"
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "origin_location_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "destination_location_id": "4ba85f64-5717-4562-b3fc-2c963f66afa7",
                    "transport_mode": "metro",
                    "started_at": "2026-08-14T08:30:00+05:30",
                    "ended_at": "2026-08-14T09:15:00+05:30",
                    "distance_km": "14.50",
                    "cost": "45.00",
                    "rating": 5,
                    "purpose": "Morning commute to office",
                    "notes": "Smooth journey with minimal crowd",
                }
            ]
        },
    )

    @field_validator("started_at", "ended_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("must include a timezone, for example 2026-08-14T08:30:00+05:30")
        return value

    @model_validator(mode="after")
    def end_must_follow_start(self) -> TripCreate:
        if self.ended_at <= self.started_at:
            raise ValueError("ended_at must be after started_at")
        return self


class TripUpdate(StrictSchema):
    origin_location_id: str | None = Field(
        default=None, min_length=36, max_length=36, description="Updated origin location UUID"
    )
    destination_location_id: str | None = Field(
        default=None, min_length=36, max_length=36, description="Updated destination location UUID"
    )
    transport_mode: TransportMode | None = Field(default=None, description="Updated transit mode")
    started_at: datetime | None = Field(
        default=None, description="Updated start time with timezone"
    )
    ended_at: datetime | None = Field(default=None, description="Updated end time with timezone")
    distance_km: Decimal | None = Field(
        default=None,
        ge=0,
        le=50_000,
        max_digits=8,
        decimal_places=2,
        description="Updated distance in kilometers",
    )
    cost: Decimal | None = Field(
        default=None,
        ge=0,
        le=1_000_000,
        max_digits=10,
        decimal_places=2,
        description="Updated trip cost",
    )
    rating: int | None = Field(
        default=None, ge=1, le=5, description="Updated satisfaction rating (1-5)"
    )
    purpose: str | None = Field(default=None, max_length=100, description="Updated journey purpose")
    notes: str | None = Field(default=None, max_length=2_000, description="Updated trip notes")

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "transport_mode": "ride_share",
                    "distance_km": "15.20",
                    "cost": "180.00",
                    "rating": 4,
                    "notes": "Rainy weather cab surge",
                }
            ]
        },
    )

    @field_validator("started_at", "ended_at")
    @classmethod
    def require_timezone_when_provided(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("must include a timezone")
        return value


class TripResponse(ResponseSchema):
    id: str = Field(description="Unique trip UUID")
    origin_location_id: str | None = Field(default=None, description="Origin location UUID")
    destination_location_id: str | None = Field(
        default=None, description="Destination location UUID"
    )
    transport_mode: TransportMode = Field(description="Mode of transit used")
    started_at: datetime = Field(description="Trip departure timestamp (UTC)")
    ended_at: datetime = Field(description="Trip arrival timestamp (UTC)")
    distance_km: Decimal = Field(description="Distance in kilometers")
    cost: Decimal = Field(description="Trip financial cost")
    rating: int | None = Field(default=None, description="User rating (1-5)")
    purpose: str | None = Field(default=None, description="Trip purpose")
    notes: str | None = Field(default=None, description="User notes")
    created_at: datetime = Field(description="Creation timestamp (UTC)")
    updated_at: datetime = Field(description="Last update timestamp (UTC)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "7fa85f64-5717-4562-b3fc-2c963f66afa9",
                    "origin_location_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "destination_location_id": "4ba85f64-5717-4562-b3fc-2c963f66afa7",
                    "transport_mode": "metro",
                    "started_at": "2026-08-14T03:00:00Z",
                    "ended_at": "2026-08-14T03:45:00Z",
                    "distance_km": "14.50",
                    "cost": "45.00",
                    "rating": 5,
                    "purpose": "Morning commute to office",
                    "notes": "Smooth journey with minimal crowd",
                    "created_at": "2026-08-14T03:45:10Z",
                    "updated_at": "2026-08-14T03:45:10Z",
                }
            ]
        },
    )
