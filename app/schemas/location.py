"""Location request and response schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import Field, model_validator

from app.models.location import LocationCategory
from app.schemas.base import ResponseSchema, StrictSchema


class LocationCreate(StrictSchema):
    name: str = Field(min_length=1, max_length=100)
    category: LocationCategory = LocationCategory.OTHER
    latitude: Decimal | None = Field(default=None, ge=-90, le=90, decimal_places=6)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180, decimal_places=6)
    notes: str | None = Field(default=None, max_length=2_000)

    @model_validator(mode="after")
    def coordinates_are_paired(self) -> LocationCreate:
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be supplied together")
        return self


class LocationUpdate(StrictSchema):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: LocationCategory | None = None
    latitude: Decimal | None = Field(default=None, ge=-90, le=90, decimal_places=6)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180, decimal_places=6)
    notes: str | None = Field(default=None, max_length=2_000)


class LocationResponse(ResponseSchema):
    id: str
    name: str
    category: LocationCategory
    latitude: Decimal | None
    longitude: Decimal | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

