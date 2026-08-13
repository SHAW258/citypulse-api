"""Reusable persistence fields."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.types import UTCDateTime


def utc_now() -> datetime:
    """Create timezone-aware UTC timestamps before passing them to the database."""

    return datetime.now(UTC)


class UUIDPrimaryKeyMixin:
    """Use application-generated UUIDs to avoid exposing sequential identifiers."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))


class TimestampMixin:
    """Add immutable creation and automatically refreshed update timestamps."""

    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
