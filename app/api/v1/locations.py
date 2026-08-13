"""Authenticated location endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import CurrentUserDependency, get_location_service
from app.schemas.location import LocationCreate, LocationResponse, LocationUpdate
from app.services.location import LocationService

router = APIRouter(prefix="/locations", tags=["Locations"])
LocationServiceDependency = Annotated[LocationService, Depends(get_location_service)]


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    payload: LocationCreate,
    current_user: CurrentUserDependency,
    location_service: LocationServiceDependency,
) -> LocationResponse:
    return LocationResponse.model_validate(await location_service.create(current_user.id, payload))


@router.get("", response_model=list[LocationResponse])
async def list_locations(
    current_user: CurrentUserDependency,
    location_service: LocationServiceDependency,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[LocationResponse]:
    locations = await location_service.list(current_user.id, offset=offset, limit=limit)
    return [LocationResponse.model_validate(location) for location in locations]


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: str,
    current_user: CurrentUserDependency,
    location_service: LocationServiceDependency,
) -> LocationResponse:
    return LocationResponse.model_validate(await location_service.get(location_id, current_user.id))


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: str,
    payload: LocationUpdate,
    current_user: CurrentUserDependency,
    location_service: LocationServiceDependency,
) -> LocationResponse:
    location = await location_service.update(location_id, current_user.id, payload)
    return LocationResponse.model_validate(location)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: str,
    current_user: CurrentUserDependency,
    location_service: LocationServiceDependency,
) -> Response:
    await location_service.delete(location_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
