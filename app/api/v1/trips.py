from datetime import date
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, Response, status

from app.api.deps import CurrentUserDependency, get_trip_service
from app.schemas.trip import TripCreate, TripResponse, TripUpdate
from app.services.trip import TripService

router = APIRouter(prefix="/trips", tags=["Trips"])
TripServiceDependency = Annotated[TripService, Depends(get_trip_service)]


@router.post(
    "",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a new trip",
    description="Records a mobility journey with distance, cost, transport mode, start/end timestamps, and optional origin/destination locations.",
    responses={
        201: {"description": "Trip logged successfully", "model": TripResponse},
        401: {"description": "Unauthorized access"},
        422: {
            "description": "Validation error (e.g. ended_at is before started_at, invalid coordinates, or unowned locations)"
        },
    },
)
async def create_trip(
    payload: Annotated[
        TripCreate,
        Body(
            openapi_examples={
                "metro_commute": {
                    "summary": "Metro Commute Example",
                    "description": "Standard public transit trip",
                    "value": {
                        "transport_mode": "metro",
                        "started_at": "2026-08-14T08:30:00+05:30",
                        "ended_at": "2026-08-14T09:15:00+05:30",
                        "distance_km": "14.50",
                        "cost": "45.00",
                        "rating": 5,
                        "purpose": "Morning commute to office",
                        "notes": "Smooth journey with minimal crowd",
                    },
                },
                "cab_ride": {
                    "summary": "Ride-share / Cab Example",
                    "description": "Peak hour ride-share journey",
                    "value": {
                        "transport_mode": "ride_share",
                        "started_at": "2026-08-14T19:00:00+05:30",
                        "ended_at": "2026-08-14T19:50:00+05:30",
                        "distance_km": "18.20",
                        "cost": "260.00",
                        "rating": 4,
                        "purpose": "Return commute",
                        "notes": "Traffic surge on expressway",
                    },
                },
            }
        ),
    ],
    current_user: CurrentUserDependency,
    trip_service: TripServiceDependency,
) -> TripResponse:
    return TripResponse.model_validate(await trip_service.create(current_user.id, payload))


@router.get(
    "",
    response_model=list[TripResponse],
    summary="List recorded trips",
    description="Retrieves a paginated and date-filtered list of mobility trips logged by the authenticated user.",
    responses={
        200: {"description": "List of trips retrieved successfully"},
        401: {"description": "Unauthorized access"},
        422: {"description": "Invalid date range parameters"},
    },
)
async def list_trips(
    current_user: CurrentUserDependency,
    trip_service: TripServiceDependency,
    offset: int = Query(default=0, ge=0, description="Pagination offset", examples=[0]),
    limit: int = Query(
        default=50, ge=1, le=100, description="Maximum trips to return", examples=[20]
    ),
    from_date: date | None = Query(
        default=None,
        description="Filter trips starting on or after this date (YYYY-MM-DD)",
        examples=["2026-08-01"],
    ),
    to_date: date | None = Query(
        default=None,
        description="Filter trips starting on or before this date (YYYY-MM-DD)",
        examples=["2026-08-14"],
    ),
) -> list[TripResponse]:
    trips = await trip_service.list(
        current_user.id,
        offset=offset,
        limit=limit,
        from_date=from_date,
        to_date=to_date,
    )
    return [TripResponse.model_validate(trip) for trip in trips]


@router.get(
    "/{trip_id}",
    response_model=TripResponse,
    summary="Get trip by ID",
    description="Fetches full details of a single trip by UUID. Ensures caller ownership.",
    responses={
        200: {"description": "Trip retrieved successfully", "model": TripResponse},
        401: {"description": "Unauthorized access"},
        404: {"description": "Trip not found or belongs to another user"},
    },
)
async def get_trip(
    trip_id: Annotated[
        str,
        Path(
            description="Trip UUID string",
            min_length=36,
            max_length=36,
            examples=["7fa85f64-5717-4562-b3fc-2c963f66afa9"],
        ),
    ],
    current_user: CurrentUserDependency,
    trip_service: TripServiceDependency,
) -> TripResponse:
    return TripResponse.model_validate(await trip_service.get(trip_id, current_user.id))


@router.patch(
    "/{trip_id}",
    response_model=TripResponse,
    summary="Update trip details",
    description="Partially updates an existing trip record with validation on timestamps, distances, and location references.",
    responses={
        200: {"description": "Trip updated successfully", "model": TripResponse},
        401: {"description": "Unauthorized access"},
        404: {"description": "Trip not found"},
        422: {"description": "Validation error"},
    },
)
async def update_trip(
    trip_id: Annotated[
        str,
        Path(
            description="Trip UUID string",
            min_length=36,
            max_length=36,
            examples=["7fa85f64-5717-4562-b3fc-2c963f66afa9"],
        ),
    ],
    payload: Annotated[
        TripUpdate,
        Body(
            openapi_examples={
                "update_cost": {
                    "summary": "Update Trip Cost and Rating",
                    "value": {
                        "cost": "50.00",
                        "rating": 5,
                        "notes": "Updated with parking toll receipt",
                    },
                }
            }
        ),
    ],
    current_user: CurrentUserDependency,
    trip_service: TripServiceDependency,
) -> TripResponse:
    trip = await trip_service.update(trip_id, current_user.id, payload)
    return TripResponse.model_validate(trip)


@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a trip",
    description="Deletes a trip record owned by the authenticated caller.",
    responses={
        204: {"description": "Trip successfully deleted"},
        401: {"description": "Unauthorized access"},
        404: {"description": "Trip not found"},
    },
)
async def delete_trip(
    trip_id: Annotated[
        str,
        Path(
            description="Trip UUID string",
            min_length=36,
            max_length=36,
            examples=["7fa85f64-5717-4562-b3fc-2c963f66afa9"],
        ),
    ],
    current_user: CurrentUserDependency,
    trip_service: TripServiceDependency,
) -> Response:
    await trip_service.delete(trip_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
