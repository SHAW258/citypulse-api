from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, Response, status

from app.api.deps import CurrentUserDependency, get_location_service
from app.schemas.location import LocationCreate, LocationResponse, LocationUpdate
from app.services.location import LocationService

router = APIRouter(prefix="/locations", tags=["Locations"])
LocationServiceDependency = Annotated[LocationService, Depends(get_location_service)]


@router.post(
    "",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new saved location",
    description="Creates a new geographic or named place associated strictly with the authenticated user.",
    responses={
        201: {"description": "Location created successfully", "model": LocationResponse},
        401: {"description": "Unauthorized access"},
        422: {"description": "Validation error (e.g. coordinates not paired)"},
    },
)
async def create_location(
    payload: Annotated[
        LocationCreate,
        Body(
            openapi_examples={
                "home": {
                    "summary": "Home Location Example",
                    "description": "Standard residential address example",
                    "value": {
                        "name": "Central Residence",
                        "category": "home",
                        "latitude": "12.971598",
                        "longitude": "77.594562",
                        "notes": "Primary apartment building near the metro station",
                    },
                },
                "work": {
                    "summary": "Office / Workplace Example",
                    "description": "Office location with custom notes",
                    "value": {
                        "name": "Tech Park HQ",
                        "category": "work",
                        "latitude": "12.935242",
                        "longitude": "77.624462",
                        "notes": "Building 3, 4th floor workspace",
                    },
                },
            }
        ),
    ],
    current_user: CurrentUserDependency,
    location_service: LocationServiceDependency,
) -> LocationResponse:
    return LocationResponse.model_validate(await location_service.create(current_user.id, payload))


@router.get(
    "",
    response_model=list[LocationResponse],
    summary="List saved locations",
    description="Retrieves a paginated list of all locations owned by the authenticated caller.",
    responses={
        200: {"description": "List of locations retrieved successfully"},
        401: {"description": "Unauthorized access"},
    },
)
async def list_locations(
    current_user: CurrentUserDependency,
    location_service: LocationServiceDependency,
    offset: int = Query(default=0, ge=0, description="Pagination offset index", examples=[0]),
    limit: int = Query(
        default=50, ge=1, le=100, description="Maximum number of items to return", examples=[20]
    ),
) -> list[LocationResponse]:
    locations = await location_service.list(current_user.id, offset=offset, limit=limit)
    return [LocationResponse.model_validate(location) for location in locations]


@router.get(
    "/{location_id}",
    response_model=LocationResponse,
    summary="Get location by ID",
    description="Fetches full details for a single saved place. Only succeeds if the place belongs to the caller.",
    responses={
        200: {"description": "Location details retrieved", "model": LocationResponse},
        401: {"description": "Unauthorized access"},
        404: {"description": "Location not found or belongs to another user"},
    },
)
async def get_location(
    location_id: Annotated[
        str,
        Path(
            description="Location UUID string",
            min_length=36,
            max_length=36,
            examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
        ),
    ],
    current_user: CurrentUserDependency,
    location_service: LocationServiceDependency,
) -> LocationResponse:
    return LocationResponse.model_validate(await location_service.get(location_id, current_user.id))


@router.patch(
    "/{location_id}",
    response_model=LocationResponse,
    summary="Update saved location",
    description="Partially updates an existing saved location. Validates paired latitude/longitude rules.",
    responses={
        200: {"description": "Location updated successfully", "model": LocationResponse},
        401: {"description": "Unauthorized access"},
        404: {"description": "Location not found"},
        422: {"description": "Validation failure"},
    },
)
async def update_location(
    location_id: Annotated[
        str,
        Path(
            description="Location UUID string",
            min_length=36,
            max_length=36,
            examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
        ),
    ],
    payload: Annotated[
        LocationUpdate,
        Body(
            openapi_examples={
                "update_name": {
                    "summary": "Update Name and Notes",
                    "value": {
                        "name": "Main Residence - Downtown",
                        "notes": "Updated gate passcode and floor details",
                    },
                }
            }
        ),
    ],
    current_user: CurrentUserDependency,
    location_service: LocationServiceDependency,
) -> LocationResponse:
    location = await location_service.update(location_id, current_user.id, payload)
    return LocationResponse.model_validate(location)


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete saved location",
    description="Deletes a location owned by the authenticated caller. Associated trips retain their records with nullified foreign keys.",
    responses={
        204: {"description": "Location successfully deleted"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Location not found"},
    },
)
async def delete_location(
    location_id: Annotated[
        str,
        Path(
            description="Location UUID string",
            min_length=36,
            max_length=36,
            examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
        ),
    ],
    current_user: CurrentUserDependency,
    location_service: LocationServiceDependency,
) -> Response:
    await location_service.delete(location_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
