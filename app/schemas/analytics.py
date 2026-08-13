"""Read-only analytics response schemas."""

from datetime import date
from decimal import Decimal

from app.models.trip import TransportMode
from app.schemas.base import StrictSchema


class SummaryResponse(StrictSchema):
    from_date: date
    to_date: date
    trip_count: int
    total_distance_km: Decimal
    total_cost: Decimal
    total_duration_minutes: int
    average_distance_km: Decimal


class TransportModeBreakdown(StrictSchema):
    mode: TransportMode
    trip_count: int
    total_distance_km: Decimal
    total_cost: Decimal
    percent_of_trips: Decimal


class DailyDistancePoint(StrictSchema):
    date: date
    trip_count: int
    total_distance_km: Decimal
    total_cost: Decimal


class OutlierResponse(StrictSchema):
    trip_id: str
    started_at: str
    distance_km: Decimal
    threshold_km: Decimal
    reason: str
