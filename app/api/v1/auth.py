from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, status

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


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new CityPulse account with a unique email and strong password. Passwords are non-reversibly hashed using Argon2id.",
    responses={
        201: {"description": "Account created successfully", "model": UserResponse},
        409: {"description": "Email or username already exists"},
        422: {"description": "Validation error (e.g. weak password or invalid email)"},
    },
)
async def register(
    payload: Annotated[
        RegisterRequest,
        Body(
            openapi_examples={
                "standard": {
                    "summary": "Standard Registration Example",
                    "description": "A valid user registration with standard email and strong password",
                    "value": {
                        "email": "user@example.com",
                        "username": "city_user01",
                        "password": "StrongPassword!2026",
                    },
                }
            }
        ),
    ],
    auth_service: AuthServiceDependency,
) -> UserResponse:
    """Create a new account. Passwords are hashed and never returned."""

    user = await auth_service.register(payload)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT token pair",
    description="Authenticates credentials and issues a short-lived access token along with a rotating single-use refresh token.",
    responses={
        200: {"description": "Authentication successful", "model": TokenResponse},
        401: {"description": "Invalid credentials or inactive account"},
        429: {"description": "Rate limit exceeded (too many sign-in attempts)"},
    },
)
async def login(
    payload: Annotated[
        LoginRequest,
        Body(
            openapi_examples={
                "standard": {
                    "summary": "Standard Login Example",
                    "description": "Log in using registered email and password",
                    "value": {
                        "email": "user@example.com",
                        "password": "StrongPassword!2026",
                    },
                }
            }
        ),
    ],
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


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate refresh token and issue new access token",
    description="Rotates a valid refresh token. The previous token is revoked immediately with automatic reuse detection.",
    responses={
        200: {"description": "Token rotated successfully", "model": TokenResponse},
        401: {"description": "Invalid, expired, or revoked refresh token"},
    },
)
async def refresh(
    payload: Annotated[
        RefreshRequest,
        Body(
            openapi_examples={
                "standard": {
                    "summary": "Token Refresh Example",
                    "description": "Submit a valid refresh JWT token to obtain a fresh token pair",
                    "value": {
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZmE4NWY2NC01NzE3LTQ1NjItYjNmYy0yYzk2M2Y2NmFmYTYiLCJqdGkiOiJmNmI5NzI2NS0xMjM0LTQ1NjctODkwMS0yMzQ1Njc4OTA5MDEiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4Njc2NTIwMCwiaWF0IjoxNzg2MTYwNDAwfQ.exampleSignature"
                    },
                }
            }
        ),
    ],
    request: Request,
    auth_service: AuthServiceDependency,
) -> TokenResponse:
    """Rotate a valid refresh token; the old refresh token becomes unusable immediately."""

    return await auth_service.refresh(
        payload.refresh_token,
        client_ip=client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Revoke active refresh token",
    description="Revokes the supplied refresh token for the authenticated user to conclude the active session.",
    responses={
        200: {"description": "Successfully signed out", "model": MessageResponse},
        401: {"description": "Unauthorized access or invalid token"},
    },
)
async def logout(
    payload: Annotated[
        LogoutRequest,
        Body(
            openapi_examples={
                "standard": {
                    "summary": "Logout Example",
                    "description": "Revoke the current refresh token",
                    "value": {
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZmE4NWY2NC01NzE3LTQ1NjItYjNmYy0yYzk2M2Y2NmFmYTYiLCJqdGkiOiJmNmI5NzI2NS0xMjM0LTQ1NjctODkwMS0yMzQ1Njc4OTA5MDEiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4Njc2NTIwMCwiaWF0IjoxNzg2MTYwNDAwfQ.exampleSignature"
                    },
                }
            }
        ),
    ],
    current_user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
) -> MessageResponse:
    """Revoke the supplied refresh token for the authenticated account."""

    await auth_service.logout(payload.refresh_token, user_id=current_user.id)
    return MessageResponse(message="Signed out successfully")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the profile details of the authenticated caller extracted from the Bearer JWT token.",
    responses={
        200: {"description": "Profile retrieved successfully", "model": UserResponse},
        401: {"description": "Missing, invalid, or expired Bearer token"},
    },
)
async def me(current_user: CurrentUserDependency) -> UserResponse:
    """Return the currently authenticated account without sensitive fields."""

    return UserResponse.model_validate(current_user)
