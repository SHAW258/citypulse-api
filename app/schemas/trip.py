"""Trip request and response schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import Field, field_validator, model_validator

from app.models.trip import TransportMode
from app.schemas.base import ResponseSchema, StrictSchema


class TripCreate(StrictSchema):
    origin_location_id: str | None = Field(default=None, min_length=36, max_length=36)
    destination_location_id: str | None = Field(default=None, min_length=36, max_length=36)
    transport_mode: TransportMode
    started_at: datetime
    ended_at: datetime
    distance_km: Decimal = Field(ge=0, le=50_000, max_digits=8, decimal_places=2)
    cost: Decimal = Field(default=Decimal("0"), ge=0, le=1_000_000, max_digits=10, decimal_places=2)
    rating: int | None = Field(default=None, ge=1, le=5)
    purpose: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=2_000)

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
    origin_location_id: str | None = Field(default=None, min_length=36, max_length=36)
    destination_location_id: str | None = Field(default=None, min_length=36, max_length=36)
    transport_mode: TransportMode | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    distance_km: Decimal | None = Field(
        default=None,
        ge=0,
        le=50_000,
        max_digits=8,
        decimal_places=2,
    )
    cost: Decimal | None = Field(default=None, ge=0, le=1_000_000, max_digits=10, decimal_places=2)
    rating: int | None = Field(default=None, ge=1, le=5)
    purpose: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=2_000)

    @field_validator("started_at", "ended_at")
    @classmethod
    def require_timezone_when_provided(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("must include a timezone")
        return value


class TripResponse(ResponseSchema):
    id: str
    origin_location_id: str | None
    destination_location_id: str | None
    transport_mode: TransportMode
    started_at: datetime
    ended_at: datetime
    distance_km: Decimal
    cost: Decimal
    rating: int | None
    purpose: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
