"""Authenticated dashboard analytics endpoints."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserDependency, get_analytics_service
from app.schemas.analytics import (
    DailyDistancePoint,
    OutlierResponse,
    SummaryResponse,
    TransportModeBreakdown,
)
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])
AnalyticsServiceDependency = Annotated[AnalyticsService, Depends(get_analytics_service)]


@router.get("/summary", response_model=SummaryResponse)
async def summary(
    current_user: CurrentUserDependency,
    analytics_service: AnalyticsServiceDependency,
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> SummaryResponse:
    return await analytics_service.summary(
        current_user.id,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/transport-modes", response_model=list[TransportModeBreakdown])
async def transport_modes(
    current_user: CurrentUserDependency,
    analytics_service: AnalyticsServiceDependency,
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> list[TransportModeBreakdown]:
    return await analytics_service.transport_modes(
        current_user.id,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/daily-distance", response_model=list[DailyDistancePoint])
async def daily_distance(
    current_user: CurrentUserDependency,
    analytics_service: AnalyticsServiceDependency,
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> list[DailyDistancePoint]:
    return await analytics_service.daily_distance(
        current_user.id,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/outliers", response_model=list[OutlierResponse])
async def distance_outliers(
    current_user: CurrentUserDependency,
    analytics_service: AnalyticsServiceDependency,
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> list[OutlierResponse]:
    return await analytics_service.distance_outliers(
        current_user.id,
        from_date=from_date,
        to_date=to_date,
    )
