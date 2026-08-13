"""Account lifecycle, token rotation, and authenticated-user resolution."""

from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    password_needs_rehash,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.user import RefreshTokenRepository, UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class AuthService:
    """Use repository dependencies to enforce authentication invariants."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.users = UserRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)

    async def register(self, payload: RegisterRequest) -> User:
        if await self.users.get_by_email(str(payload.email)):
            raise ConflictError("An account with that email already exists")
        if await self.users.get_by_username(payload.username):
            raise ConflictError("That username is already in use")

        user = User(
            email=str(payload.email),
            username=payload.username,
            password_hash=hash_password(payload.password),
        )
        try:
            await self.users.add(user)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictError("An account with those details already exists") from exc
        return user

    async def login(
        self,
        payload: LoginRequest,
        *,
        client_ip: str | None,
        user_agent: str | None,
    ) -> TokenResponse:
        user = await self.users.get_by_email(str(payload.email))
        password_matches = user is not None and verify_password(
            payload.password,
            user.password_hash,
        )
        if user is None or not password_matches or not user.is_active:
            # Deliberately generic to avoid account enumeration.
            raise AuthenticationError("Incorrect email or password")

        if password_needs_rehash(user.password_hash):
            user.password_hash = hash_password(payload.password)
        await self.users.record_login(user, _utc_now())
        response = await self._issue_token_pair(user, client_ip=client_ip, user_agent=user_agent)
        await self.session.commit()
        return response

    async def refresh(
        self,
        raw_refresh_token: str,
        *,
        client_ip: str | None,
        user_agent: str | None,
    ) -> TokenResponse:
        try:
            claims = decode_token(
                token=raw_refresh_token,
                expected_type="refresh",
                settings=self.settings,
            )
        except TokenError as exc:
            raise AuthenticationError("Invalid refresh token") from exc

        stored_token = await self.refresh_tokens.get_by_token_id(claims["jti"])
        if stored_token is None or stored_token.user_id != claims["sub"]:
            raise AuthenticationError("Invalid refresh token")

        now = _utc_now()
        if stored_token.revoked_at is not None:
            # A reused rotated token signals possible theft; invalidate the account's sessions.
            await self.refresh_tokens.revoke_all_for_user(stored_token.user_id, now)
            await self.session.commit()
            raise AuthenticationError("Refresh token is no longer valid")
        if _as_utc(stored_token.expires_at) <= now:
            await self.refresh_tokens.revoke(stored_token, now)
            await self.session.commit()
            raise AuthenticationError("Refresh token is expired")

        user = await self.users.get_by_id(stored_token.user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid refresh token")

        await self.refresh_tokens.revoke(stored_token, now)
        response = await self._issue_token_pair(user, client_ip=client_ip, user_agent=user_agent)
        await self.session.commit()
        return response

    async def logout(self, raw_refresh_token: str, *, user_id: str) -> None:
        try:
            claims = decode_token(
                token=raw_refresh_token,
                expected_type="refresh",
                settings=self.settings,
            )
        except TokenError as exc:
            raise AuthenticationError("Invalid refresh token") from exc
        if claims["sub"] != user_id:
            raise AuthenticationError("Invalid refresh token")

        stored_token = await self.refresh_tokens.get_by_token_id(claims["jti"])
        if stored_token and stored_token.user_id == user_id and stored_token.revoked_at is None:
            await self.refresh_tokens.revoke(stored_token, _utc_now())
            await self.session.commit()

    async def get_current_user(self, raw_access_token: str) -> User:
        try:
            claims = decode_token(
                token=raw_access_token,
                expected_type="access",
                settings=self.settings,
            )
        except TokenError as exc:
            raise AuthenticationError("Could not validate credentials") from exc

        user = await self.users.get_by_id(claims["sub"])
        if user is None or not user.is_active:
            raise AuthenticationError("Could not validate credentials")
        return user

    async def _issue_token_pair(
        self,
        user: User,
        *,
        client_ip: str | None,
        user_agent: str | None,
    ) -> TokenResponse:
        access_token = create_access_token(
            user_id=user.id,
            is_superuser=user.is_superuser,
            settings=self.settings,
        )
        refresh_token, token_id, expires_at = create_refresh_token(
            user_id=user.id,
            settings=self.settings,
        )
        await self.refresh_tokens.add(
            RefreshToken(
                token_id=token_id,
                user_id=user.id,
                expires_at=expires_at,
                client_ip=client_ip[:45] if client_ip else None,
                user_agent=user_agent[:512] if user_agent else None,
            )
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_in=self.settings.access_token_expire_minutes * 60,
            user=UserResponse.model_validate(user),
        )
