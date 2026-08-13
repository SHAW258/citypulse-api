"""Authentication request and public response schemas."""

import re
from datetime import datetime

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import ResponseSchema, StrictSchema

_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


class RegisterRequest(StrictSchema):
    email: EmailStr
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=12, max_length=128)

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
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return value.lower()


class RefreshRequest(StrictSchema):
    refresh_token: str = Field(min_length=20, max_length=4_096)


class LogoutRequest(StrictSchema):
    refresh_token: str = Field(min_length=20, max_length=4_096)


class UserResponse(ResponseSchema):
    id: str
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime


class TokenResponse(StrictSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_in: int
    user: UserResponse


class MessageResponse(StrictSchema):
    message: str

