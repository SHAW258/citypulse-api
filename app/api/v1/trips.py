"""Authenticated trip endpoints."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import CurrentUserDependency, get_trip_service
from app.schemas.trip import TripCreate, TripResponse, TripUpdate
from app.services.trip import TripService

router = APIRouter(prefix="/trips", tags=["Trips"])
TripServiceDependency = Annotated[TripService, Depends(get_trip_service)]


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    payload: TripCreate,
    current_user: CurrentUserDependency,
    trip_service: TripServiceDependency,
) -> TripResponse:
    return TripResponse.model_validate(await trip_service.create(current_user.id, payload))


@router.get("", response_model=list[TripResponse])
async def list_trips(
    current_user: CurrentUserDependency,
    trip_service: TripServiceDependency,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> list[TripResponse]:
    trips = await trip_service.list(
        current_user.id,
        offset=offset,
        limit=limit,
        from_date=from_date,
        to_date=to_date,
    )
    return [TripResponse.model_validate(trip) for trip in trips]


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: str,
    current_user: CurrentUserDependency,
    trip_service: TripServiceDependency,
) -> TripResponse:
    return TripResponse.model_validate(await trip_service.get(trip_id, current_user.id))


@router.patch("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: str,
    payload: TripUpdate,
    current_user: CurrentUserDependency,
    trip_service: TripServiceDependency,
) -> TripResponse:
    trip = await trip_service.update(trip_id, current_user.id, payload)
    return TripResponse.model_validate(trip)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: str,
    current_user: CurrentUserDependency,
    trip_service: TripServiceDependency,
) -> Response:
    await trip_service.delete(trip_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
