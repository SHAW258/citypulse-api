"""FastAPI dependency-injection providers."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError
from app.db.session import get_db_session
from app.models.user import User
from app.services.analytics import AnalyticsService
from app.services.auth import AuthService
from app.services.location import LocationService
from app.services.trip import TripService

bearer_scheme = HTTPBearer(auto_error=False, scheme_name="Bearer Authentication")

SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]
SettingsDependency = Annotated[Settings, Depends(get_settings)]


def get_auth_service(
    session: SessionDependency,
    settings: SettingsDependency,
) -> AuthService:
    return AuthService(session, settings)


def get_location_service(session: SessionDependency) -> LocationService:
    return LocationService(session)


def get_trip_service(session: SessionDependency) -> TripService:
    return TripService(session)


def get_analytics_service(session: SessionDependency) -> AnalyticsService:
    return AnalyticsService(session)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return await auth_service.get_current_user(credentials.credentials)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


CurrentUserDependency = Annotated[User, Depends(get_current_user)]
