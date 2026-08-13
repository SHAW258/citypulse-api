"""Trip business rules and ownership-safe CRUD."""

from datetime import UTC, date, datetime, time

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationDomainError
from app.models.trip import Trip
from app.repositories.location import LocationRepository
from app.repositories.trip import TripRepository
from app.schemas.trip import TripCreate, TripUpdate


def _to_utc(value: datetime) -> datetime:
    """Normalize incoming timezone-aware datetimes before persistence."""

    return value.astimezone(UTC).replace(tzinfo=None)


class TripService:
    """Ensure trips and referenced locations always belong to the same user."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.trips = TripRepository(session)
        self.locations = LocationRepository(session)

    async def create(self, user_id: str, payload: TripCreate) -> Trip:
        await self._validate_location_ids(
            user_id,
            payload.origin_location_id,
            payload.destination_location_id,
        )
        trip = Trip(
            user_id=user_id,
            origin_location_id=payload.origin_location_id,
            destination_location_id=payload.destination_location_id,
            transport_mode=payload.transport_mode,
            started_at=_to_utc(payload.started_at),
            ended_at=_to_utc(payload.ended_at),
            distance_km=payload.distance_km,
            cost=payload.cost,
            rating=payload.rating,
            purpose=payload.purpose,
            notes=payload.notes,
        )
        await self.trips.add(trip)
        await self.session.commit()
        await self.session.refresh(trip)
        return trip

    async def list(
        self,
        user_id: str,
        *,
        offset: int,
        limit: int,
        from_date: date | None,
        to_date: date | None,
    ) -> list[Trip]:
        start, end = self._date_bounds(from_date, to_date)
        return await self.trips.list_for_user(
            user_id,
            offset=offset,
            limit=limit,
            start_date=start,
            end_date=end,
        )

    async def get(self, trip_id: str, user_id: str) -> Trip:
        trip = await self.trips.get_for_user(trip_id, user_id)
        if trip is None:
            raise NotFoundError("Trip not found")
        return trip

    async def update(self, trip_id: str, user_id: str, payload: TripUpdate) -> Trip:
        trip = await self.get(trip_id, user_id)
        changes = payload.model_dump(exclude_unset=True)
        origin_id = changes.get("origin_location_id", trip.origin_location_id)
        destination_id = changes.get("destination_location_id", trip.destination_location_id)
        await self._validate_location_ids(user_id, origin_id, destination_id)

        proposed_started = changes.get("started_at", trip.started_at)
        proposed_ended = changes.get("ended_at", trip.ended_at)
        proposed_started = (
            _to_utc(proposed_started) if proposed_started.tzinfo else proposed_started
        )
        proposed_ended = _to_utc(proposed_ended) if proposed_ended.tzinfo else proposed_ended
        if proposed_ended <= proposed_started:
            raise ValidationDomainError("ended_at must be after started_at")

        for field, value in changes.items():
            if field in {"started_at", "ended_at"}:
                value = _to_utc(value)
            setattr(trip, field, value)
        await self.session.commit()
        await self.session.refresh(trip)
        return trip

    async def delete(self, trip_id: str, user_id: str) -> None:
        trip = await self.get(trip_id, user_id)
        await self.trips.delete(trip)
        await self.session.commit()

    async def _validate_location_ids(
        self,
        user_id: str,
        origin_location_id: str | None,
        destination_location_id: str | None,
    ) -> None:
        if origin_location_id and origin_location_id == destination_location_id:
            raise ValidationDomainError("origin and destination must be different locations")
        for location_id in (origin_location_id, destination_location_id):
            if location_id and await self.locations.get_for_user(location_id, user_id) is None:
                # Treat another user's identifier as absent to avoid confirming its existence.
                raise ValidationDomainError("One of the selected locations is unavailable")

    @staticmethod
    def _date_bounds(
        from_date: date | None,
        to_date: date | None,
    ) -> tuple[datetime | None, datetime | None]:
        if from_date and to_date and from_date > to_date:
            raise ValidationDomainError("from_date must not be after to_date")
        start = datetime.combine(from_date, time.min) if from_date else None
        end = datetime.combine(to_date, time.max) if to_date else None
        return start, end
