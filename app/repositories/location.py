"""Location persistence operations scoped to an owner."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.location import Location


class LocationRepository:
    """Restrict every location lookup to its authenticated owner."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_user(self, user_id: str, *, offset: int, limit: int) -> list[Location]:
        statement = (
            select(Location)
            .where(Location.user_id == user_id)
            .order_by(Location.name.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(await self.session.scalars(statement))

    async def get_for_user(self, location_id: str, user_id: str) -> Location | None:
        statement = select(Location).where(Location.id == location_id, Location.user_id == user_id)
        return await self.session.scalar(statement)

    async def add(self, location: Location) -> Location:
        self.session.add(location)
        await self.session.flush()
        return location

    async def delete(self, location: Location) -> None:
        await self.session.delete(location)
        await self.session.flush()
