"""Authentication request and public response schemas."""

import re
from datetime import datetime

from pydantic import ConfigDict, EmailStr, Field, field_validator

from app.schemas.base import ResponseSchema, StrictSchema

_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


class RegisterRequest(StrictSchema):
    email: EmailStr = Field(description="Unique email address for registration")
    username: str = Field(
        min_length=3, max_length=32, description="Unique account username (3-32 characters)"
    )
    password: str = Field(
        min_length=12,
        max_length=128,
        description="Strong password containing uppercase, lowercase, digit, and symbol",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "email": "user@example.com",
                    "username": "city_user01",
                    "password": "StrongPassword!2026",
                }
            ]
        },
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return value.lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not _USERNAME_PATTERN.fullmatch(value):
            raise ValueError("may contain only letters, numbers, dots, hyphens, and underscores")
        return value

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        checks = (
            any(character.islower() for character in value),
            any(character.isupper() for character in value),
            any(character.isdigit() for character in value),
            any(not character.isalnum() for character in value),
        )
        if not all(checks):
            raise ValueError("must include upper, lower, number, and symbol characters")
        return value


class LoginRequest(StrictSchema):
    email: EmailStr = Field(description="Registered account email address")
    password: str = Field(min_length=1, max_length=128, description="Account password")

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "StrongPassword!2026",
                }
            ]
        },
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return value.lower()


class RefreshRequest(StrictSchema):
    refresh_token: str = Field(
        min_length=20,
        max_length=4_096,
        description="Valid rotating refresh JWT token string",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3OC1mZWRjLWJhOTgtNzY1NC0zMjEwZmVkY2JhOTgiLCJqdGkiOiJmNmI5NzI2NS0xMjM0LTQ1NjctODkwMS0yMzQ1Njc4OTA5MDEiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4Njc2NTIwMCwiaWF0IjoxNzg2MTYwNDAwfQ.exampleSignature"
                }
            ]
        },
    )


class LogoutRequest(StrictSchema):
    refresh_token: str = Field(
        min_length=20,
        max_length=4_096,
        description="Active refresh token to revoke on sign out",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3OC1mZWRjLWJhOTgtNzY1NC0zMjEwZmVkY2JhOTgiLCJqdGkiOiJmNmI5NzI2NS0xMjM0LTQ1NjctODkwMS0yMzQ1Njc4OTA5MDEiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4Njc2NTIwMCwiaWF0IjoxNzg2MTYwNDAwfQ.exampleSignature"
                }
            ]
        },
    )


class UserResponse(ResponseSchema):
    id: str = Field(description="Unique User UUID")
    email: EmailStr = Field(description="User email address")
    username: str = Field(description="User account handle")
    is_active: bool = Field(description="Whether the user account is active")
    created_at: datetime = Field(description="Account creation timestamp (UTC)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "email": "user@example.com",
                    "username": "city_user01",
                    "is_active": True,
                    "created_at": "2026-08-14T08:00:00Z",
                }
            ]
        },
    )


class TokenResponse(StrictSchema):
    access_token: str = Field(description="Short-lived signed JWT access token")
    refresh_token: str = Field(description="Rotating single-use refresh JWT token")
    token_type: str = Field(default="bearer", description="Authentication token type")
    access_token_expires_in: int = Field(description="Access token expiration window in seconds")
    user: UserResponse = Field(description="Authenticated user profile details")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZmE4NWY2NC01NzE3LTQ1NjItYjNmYy0yYzk2M2Y2NmFmYTYiLCJqdGkiOiIxMjM0NTY3OC0xMjM0LTU2NzgtMTIzNC01Njc4MTIzNDU2NzgiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg2MTYxMzAwLCJpYXQiOjE3ODYxNjA0MDB9.exampleAccessSignature",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZmE4NWY2NC01NzE3LTQ1NjItYjNmYy0yYzk2M2Y2NmFmYTYiLCJqdGkiOiJmNmI5NzI2NS0xMjM0LTQ1NjctODkwMS0yMzQ1Njc4OTA5MDEiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4Njc2NTIwMCwiaWF0IjoxNzg2MTYwNDAwfQ.exampleRefreshSignature",
                    "token_type": "bearer",
                    "access_token_expires_in": 900,
                    "user": {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "email": "user@example.com",
                        "username": "city_user01",
                        "is_active": True,
                        "created_at": "2026-08-14T08:00:00Z",
                    },
                }
            ]
        },
    )


class MessageResponse(StrictSchema):
    message: str = Field(description="Operation confirmation message")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"message": "Signed out successfully"}]},
    )
