"""Read-only analytics response schemas."""

import datetime as dt
from decimal import Decimal

from pydantic import ConfigDict, Field

from app.models.trip import TransportMode
from app.schemas.base import StrictSchema


class SummaryResponse(StrictSchema):
    from_date: dt.date = Field(description="Start boundary date for the aggregation window")
    to_date: dt.date = Field(description="End boundary date for the aggregation window")
    trip_count: int = Field(description="Total count of completed trips")
    total_distance_km: Decimal = Field(description="Sum of all trip distances in kilometers")
    total_cost: Decimal = Field(description="Total monetary expense across all recorded trips")
    total_duration_minutes: int = Field(description="Total transit duration in minutes")
    average_distance_km: Decimal = Field(description="Mean distance per trip")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "from_date": "2026-08-01",
                    "to_date": "2026-08-14",
                    "trip_count": 28,
                    "total_distance_km": "342.50",
                    "total_cost": "1250.00",
                    "total_duration_minutes": 890,
                    "average_distance_km": "12.23",
                }
            ]
        },
    )


class TransportModeBreakdown(StrictSchema):
    mode: TransportMode = Field(description="Mode of transportation")
    trip_count: int = Field(description="Number of trips logged using this mode")
    total_distance_km: Decimal = Field(description="Total kilometers traveled via this mode")
    total_cost: Decimal = Field(description="Total expenditure via this mode")
    percent_of_trips: Decimal = Field(description="Percentage share of total recorded trips")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "mode": "metro",
                    "trip_count": 14,
                    "total_distance_km": "196.00",
                    "total_cost": "630.00",
                    "percent_of_trips": "50.00",
                }
            ]
        },
    )


class DailyDistancePoint(StrictSchema):
    date: dt.date = Field(description="Date for the recorded daily distance")
    trip_count: int = Field(description="Number of trips logged on this date")
    total_distance_km: Decimal = Field(description="Total kilometers logged on this date")
    total_cost: Decimal = Field(description="Total daily transport expenditure")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "date": "2026-08-14",
                    "trip_count": 2,
                    "total_distance_km": "29.00",
                    "total_cost": "90.00",
                }
            ]
        },
    )


class OutlierResponse(StrictSchema):
    trip_id: str = Field(description="Unique trip UUID flagged as statistical outlier")
    started_at: str = Field(description="Timestamp when the trip started")
    distance_km: Decimal = Field(description="Observed distance for the journey")
    threshold_km: Decimal = Field(
        description="Calculated statistical outlier threshold (mean + 2*std)"
    )
    reason: str = Field(description="Explanation of the anomalous metric")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "trip_id": "7fa85f64-5717-4562-b3fc-2c963f66afa9",
                    "started_at": "2026-08-12T06:00:00Z",
                    "distance_km": "85.00",
                    "threshold_km": "45.50",
                    "reason": "Trip distance (85.00 km) exceeds statistical boundary (45.50 km)",
                }
            ]
        },
    )
