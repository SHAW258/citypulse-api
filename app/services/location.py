"""Location business rules, including coordinate privacy controls."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationDomainError
from app.models.location import Location
from app.repositories.location import LocationRepository
from app.schemas.location import LocationCreate, LocationUpdate


class LocationService:
    """Perform safe CRUD on locations owned by the current user."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.locations = LocationRepository(session)

    async def create(self, user_id: str, payload: LocationCreate) -> Location:
        location = Location(user_id=user_id, **payload.model_dump())
        await self.locations.add(location)
        await self.session.commit()
        await self.session.refresh(location)
        return location

    async def list(self, user_id: str, *, offset: int, limit: int) -> list[Location]:
        return await self.locations.list_for_user(user_id, offset=offset, limit=limit)

    async def get(self, location_id: str, user_id: str) -> Location:
        location = await self.locations.get_for_user(location_id, user_id)
        if location is None:
            raise NotFoundError("Location not found")
        return location

    async def update(self, location_id: str, user_id: str, payload: LocationUpdate) -> Location:
        location = await self.get(location_id, user_id)
        changes = payload.model_dump(exclude_unset=True)
        coordinate_fields = {"latitude", "longitude"}
        if coordinate_fields.intersection(changes):
            proposed_latitude = changes.get("latitude", location.latitude)
            proposed_longitude = changes.get("longitude", location.longitude)
            if (proposed_latitude is None) != (proposed_longitude is None):
                raise ValidationDomainError("latitude and longitude must be updated together")
        for field, value in changes.items():
            setattr(location, field, value)
        await self.session.commit()
        await self.session.refresh(location)
        return location

    async def delete(self, location_id: str, user_id: str) -> None:
        location = await self.get(location_id, user_id)
        await self.locations.delete(location)
        await self.session.commit()
