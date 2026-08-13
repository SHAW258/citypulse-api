"""User-scoped descriptive analytics ready to feed the Android dashboard."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationDomainError
from app.models.trip import TransportMode, Trip
from app.schemas.analytics import (
    DailyDistancePoint,
    OutlierResponse,
    SummaryResponse,
    TransportModeBreakdown,
)

_ZERO = Decimal("0")
_TWO_DP = Decimal("0.01")


class AnalyticsService:
    """Derive bounded, per-user metrics from the same transactional data used by EDA."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def summary(
        self,
        user_id: str,
        *,
        from_date: date | None,
        to_date: date | None,
    ) -> SummaryResponse:
        start, end, selected_from, selected_to = self._range(from_date, to_date)
        trips = await self._trips_for_range(user_id, start, end)
        total_distance = sum((trip.distance_km for trip in trips), start=_ZERO)
        total_cost = sum((trip.cost for trip in trips), start=_ZERO)
        total_seconds = sum((trip.ended_at - trip.started_at).total_seconds() for trip in trips)
        count = len(trips)
        average = total_distance / count if count else _ZERO
        return SummaryResponse(
            from_date=selected_from,
            to_date=selected_to,
            trip_count=count,
            total_distance_km=self._round(total_distance),
            total_cost=self._round(total_cost),
            total_duration_minutes=round(total_seconds / 60),
            average_distance_km=self._round(average),
        )

    async def transport_modes(
        self,
        user_id: str,
        *,
        from_date: date | None,
        to_date: date | None,
    ) -> list[TransportModeBreakdown]:
        start, end, _, _ = self._range(from_date, to_date)
        trips = await self._trips_for_range(user_id, start, end)
        buckets: dict[TransportMode, list[Trip]] = defaultdict(list)
        for trip in trips:
            buckets[trip.transport_mode].append(trip)
        total_count = len(trips)
        return [
            TransportModeBreakdown(
                mode=mode,
                trip_count=len(mode_trips),
                total_distance_km=self._round(
                    sum((trip.distance_km for trip in mode_trips), _ZERO)
                ),
                total_cost=self._round(sum((trip.cost for trip in mode_trips), _ZERO)),
                percent_of_trips=self._round(
                    Decimal(len(mode_trips) * 100) / total_count if total_count else _ZERO
                ),
            )
            for mode, mode_trips in sorted(buckets.items(), key=lambda item: item[0].value)
        ]

    async def daily_distance(
        self,
        user_id: str,
        *,
        from_date: date | None,
        to_date: date | None,
    ) -> list[DailyDistancePoint]:
        start, end, _, _ = self._range(from_date, to_date)
        trips = await self._trips_for_range(user_id, start, end)
        buckets: dict[date, list[Trip]] = defaultdict(list)
        for trip in trips:
            buckets[trip.started_at.date()].append(trip)
        return [
            DailyDistancePoint(
                date=trip_date,
                trip_count=len(day_trips),
                total_distance_km=self._round(sum((trip.distance_km for trip in day_trips), _ZERO)),
                total_cost=self._round(sum((trip.cost for trip in day_trips), _ZERO)),
            )
            for trip_date, day_trips in sorted(buckets.items())
        ]

    async def distance_outliers(
        self,
        user_id: str,
        *,
        from_date: date | None,
        to_date: date | None,
    ) -> list[OutlierResponse]:
        start, end, _, _ = self._range(from_date, to_date)
        trips = await self._trips_for_range(user_id, start, end)
        if len(trips) < 4:
            return []
        values = sorted(float(trip.distance_km) for trip in trips)
        q1 = self._percentile(values, 25)
        q3 = self._percentile(values, 75)
        threshold = q3 + 1.5 * (q3 - q1)
        threshold_decimal = self._round(Decimal(str(threshold)))
        return [
            OutlierResponse(
                trip_id=trip.id,
                started_at=trip.started_at.isoformat(),
                distance_km=trip.distance_km,
                threshold_km=threshold_decimal,
                reason="Distance exceeds the IQR outlier threshold",
            )
            for trip in trips
            if trip.distance_km > threshold_decimal
        ]

    async def _trips_for_range(self, user_id: str, start: datetime, end: datetime) -> list[Trip]:
        statement = (
            select(Trip)
            .where(Trip.user_id == user_id, Trip.started_at >= start, Trip.started_at <= end)
            .order_by(Trip.started_at.asc())
        )
        return list(await self.session.scalars(statement))

    @staticmethod
    def _range(
        from_date: date | None,
        to_date: date | None,
    ) -> tuple[datetime, datetime, date, date]:
        selected_to = to_date or date.today()
        selected_from = from_date or selected_to - timedelta(days=29)
        if selected_from > selected_to:
            raise ValidationDomainError("from_date must not be after to_date")
        if (selected_to - selected_from).days > 366:
            raise ValidationDomainError("Analytics range cannot exceed 367 days")
        return (
            datetime.combine(selected_from, time.min),
            datetime.combine(selected_to, time.max),
            selected_from,
            selected_to,
        )

    @staticmethod
    def _round(value: Decimal) -> Decimal:
        return value.quantize(_TWO_DP, rounding=ROUND_HALF_UP)

    @staticmethod
    def _percentile(values: list[float], percentile: int) -> float:
        """Linear-interpolation percentile without requiring a scientific stack at runtime."""

        position = (len(values) - 1) * percentile / 100
        lower = int(position)
        upper = min(lower + 1, len(values) - 1)
        fraction = position - lower
        return values[lower] + (values[upper] - values[lower]) * fraction
