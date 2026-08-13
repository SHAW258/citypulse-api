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


@router.get(
    "/summary",
    response_model=SummaryResponse,
    summary="Get overall mobility summary metrics",
    description="Computes aggregate metrics (total trips, distance, cost, transit duration, average distance) over a specified date range.",
    responses={
        200: {"description": "Summary metrics computed successfully", "model": SummaryResponse},
        401: {"description": "Unauthorized access"},
        422: {
            "description": "Validation error (e.g. invalid date order or range exceeding 367 days)"
        },
    },
)
async def summary(
    current_user: CurrentUserDependency,
    analytics_service: AnalyticsServiceDependency,
    from_date: date | None = Query(
        default=None,
        description="Start date for analytics window (YYYY-MM-DD)",
        examples=["2026-08-01"],
    ),
    to_date: date | None = Query(
        default=None,
        description="End date for analytics window (YYYY-MM-DD)",
        examples=["2026-08-14"],
    ),
) -> SummaryResponse:
    return await analytics_service.summary(
        current_user.id,
        from_date=from_date,
        to_date=to_date,
    )


@router.get(
    "/transport-modes",
    response_model=list[TransportModeBreakdown],
    summary="Get breakdown by transportation mode",
    description="Returns aggregate trip counts, total distance, expenditure, and trip share percentages for each transportation mode.",
    responses={
        200: {"description": "Transport mode breakdown computed successfully"},
        401: {"description": "Unauthorized access"},
        422: {"description": "Invalid date range parameters"},
    },
)
async def transport_modes(
    current_user: CurrentUserDependency,
    analytics_service: AnalyticsServiceDependency,
    from_date: date | None = Query(
        default=None, description="Start date (YYYY-MM-DD)", examples=["2026-08-01"]
    ),
    to_date: date | None = Query(
        default=None, description="End date (YYYY-MM-DD)", examples=["2026-08-14"]
    ),
) -> list[TransportModeBreakdown]:
    return await analytics_service.transport_modes(
        current_user.id,
        from_date=from_date,
        to_date=to_date,
    )


@router.get(
    "/daily-distance",
    response_model=list[DailyDistancePoint],
    summary="Get daily distance time series",
    description="Returns daily aggregates of mobility distance and financial cost across each day in the selected window.",
    responses={
        200: {"description": "Daily distance points computed"},
        401: {"description": "Unauthorized access"},
        422: {"description": "Invalid date range parameters"},
    },
)
async def daily_distance(
    current_user: CurrentUserDependency,
    analytics_service: AnalyticsServiceDependency,
    from_date: date | None = Query(
        default=None, description="Start date (YYYY-MM-DD)", examples=["2026-08-01"]
    ),
    to_date: date | None = Query(
        default=None, description="End date (YYYY-MM-DD)", examples=["2026-08-14"]
    ),
) -> list[DailyDistancePoint]:
    return await analytics_service.daily_distance(
        current_user.id,
        from_date=from_date,
        to_date=to_date,
    )


@router.get(
    "/outliers",
    response_model=list[OutlierResponse],
    summary="Detect statistical mobility outliers",
    description="Calculates statistical anomalies in distance using Interquartile Range (IQR) methods across user trip history.",
    responses={
        200: {"description": "Outlier detection completed"},
        401: {"description": "Unauthorized access"},
        422: {"description": "Invalid date range parameters"},
    },
)
async def distance_outliers(
    current_user: CurrentUserDependency,
    analytics_service: AnalyticsServiceDependency,
    from_date: date | None = Query(
        default=None, description="Start date (YYYY-MM-DD)", examples=["2026-08-01"]
    ),
    to_date: date | None = Query(
        default=None, description="End date (YYYY-MM-DD)", examples=["2026-08-14"]
    ),
) -> list[OutlierResponse]:
    return await analytics_service.distance_outliers(
        current_user.id,
        from_date=from_date,
        to_date=to_date,
    )
