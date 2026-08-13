"""User and refresh-token persistence operations."""

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.models.user import User


class UserRepository:
    """Query and mutate accounts without leaking SQL into services."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: str) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email.lower())
        return await self.session.scalar(statement)

    async def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return await self.session.scalar(statement)

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def record_login(self, user: User, logged_in_at: datetime) -> None:
        user.last_login_at = logged_in_at
        await self.session.flush()


class RefreshTokenRepository:
    """Store only refresh-token identifiers, enabling server-side revocation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, token: RefreshToken) -> RefreshToken:
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_by_token_id(self, token_id: str) -> RefreshToken | None:
        statement = select(RefreshToken).where(RefreshToken.token_id == token_id)
        return await self.session.scalar(statement)

    async def revoke(self, token: RefreshToken, revoked_at: datetime) -> None:
        token.revoked_at = revoked_at
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: str, revoked_at: datetime) -> None:
        statement = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )
        await self.session.execute(statement)

