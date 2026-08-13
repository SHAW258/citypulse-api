"""Account registration, sign-in, refresh, and logout endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.api.deps import CurrentUserDependency, get_auth_service
from app.middleware.rate_limit import client_ip, login_rate_limiter
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, auth_service: AuthServiceDependency) -> UserResponse:
    """Create a new account. Passwords are hashed and never returned."""

    user = await auth_service.register(payload)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    auth_service: AuthServiceDependency,
) -> TokenResponse:
    """Authenticate with email and password, then return an access/refresh token pair."""

    ip = client_ip(request)
    await login_rate_limiter.enforce(
        f"login:{ip}",
        limit=auth_service.settings.login_rate_limit_per_minute,
    )
    return await auth_service.login(
        payload,
        client_ip=ip,
        user_agent=request.headers.get("user-agent"),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    auth_service: AuthServiceDependency,
) -> TokenResponse:
    """Rotate a valid refresh token; the old refresh token becomes unusable immediately."""

    return await auth_service.refresh(
        payload.refresh_token,
        client_ip=client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: LogoutRequest,
    current_user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
) -> MessageResponse:
    """Revoke the supplied refresh token for the authenticated account."""

    await auth_service.logout(payload.refresh_token, user_id=current_user.id)
    return MessageResponse(message="Signed out successfully")


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUserDependency) -> UserResponse:
    """Return the currently authenticated account without sensitive fields."""

    return UserResponse.model_validate(current_user)
