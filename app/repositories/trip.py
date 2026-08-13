"""Trip persistence operations scoped to an owner."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip


class TripRepository:
    """Query journeys without ever accepting an unscoped trip identifier."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_user(
        self,
        user_id: str,
        *,
        offset: int,
        limit: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Trip]:
        statement = select(Trip).where(Trip.user_id == user_id)
        if start_date is not None:
            statement = statement.where(Trip.started_at >= start_date)
        if end_date is not None:
            statement = statement.where(Trip.started_at <= end_date)
        statement = statement.order_by(Trip.started_at.desc()).offset(offset).limit(limit)
        return list(await self.session.scalars(statement))

    async def get_for_user(self, trip_id: str, user_id: str) -> Trip | None:
        statement = select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id)
        return await self.session.scalar(statement)

    async def add(self, trip: Trip) -> Trip:
        self.session.add(trip)
        await self.session.flush()
        return trip

    async def delete(self, trip: Trip) -> None:
        await self.session.delete(trip)
        await self.session.flush()
