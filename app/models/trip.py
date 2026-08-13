"""Mobility event persistence model, designed for later EDA extraction."""

from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DECIMAL,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.location import Location
    from app.models.user import User


class TransportMode(enum.StrEnum):
    WALK = "walk"
    BIKE = "bike"
    BUS = "bus"
    TRAIN = "train"
    METRO = "metro"
    CAR = "car"
    AUTO = "auto"
    RIDE_SHARE = "ride_share"
    OTHER = "other"


class Trip(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One recorded journey, owned by exactly one user."""

    __tablename__ = "trips"
    __table_args__ = (
        CheckConstraint("distance_km >= 0", name="ck_trips_distance_non_negative"),
        CheckConstraint("cost >= 0", name="ck_trips_cost_non_negative"),
        CheckConstraint("rating IS NULL OR rating BETWEEN 1 AND 5", name="ck_trips_rating_range"),
        Index("ix_trips_user_started_at", "user_id", "started_at"),
        Index("ix_trips_user_transport", "user_id", "transport_mode"),
    )

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    origin_location_id: Mapped[str | None] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    destination_location_id: Mapped[str | None] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    transport_mode: Mapped[TransportMode] = mapped_column(
        Enum(TransportMode, native_enum=False, length=20),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    ended_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    distance_km: Mapped[Decimal] = mapped_column(DECIMAL(8, 2), nullable=False)
    cost: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=Decimal("0"), nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    purpose: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    owner: Mapped[User] = relationship(back_populates="trips")
    origin_location: Mapped[Location | None] = relationship(
        foreign_keys=[origin_location_id],
        back_populates="origin_trips",
    )
    destination_location: Mapped[Location | None] = relationship(
        foreign_keys=[destination_location_id],
        back_populates="destination_trips",
    )
