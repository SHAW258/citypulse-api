"""Saved, user-owned places with intentionally limited metadata."""

from __future__ import annotations

import enum
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.trip import Trip
    from app.models.user import User


class LocationCategory(enum.StrEnum):
    HOME = "home"
    WORK = "work"
    COLLEGE = "college"
    FOOD = "food"
    LEISURE = "leisure"
    SHOPPING = "shopping"
    HEALTH = "health"
    OTHER = "other"


class Location(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A saved place belonging to a single account."""

    __tablename__ = "locations"
    __table_args__ = (Index("ix_locations_user_category", "user_id", "category"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[LocationCategory] = mapped_column(
        Enum(LocationCategory, native_enum=False, length=20),
        default=LocationCategory.OTHER,
        nullable=False,
    )
    latitude: Mapped[Decimal | None] = mapped_column(DECIMAL(8, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(DECIMAL(9, 6), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    owner: Mapped[User] = relationship(back_populates="locations")
    origin_trips: Mapped[list[Trip]] = relationship(
        foreign_keys="Trip.origin_location_id",
        back_populates="origin_location",
    )
    destination_trips: Mapped[list[Trip]] = relationship(
        foreign_keys="Trip.destination_location_id",
        back_populates="destination_location",
    )
