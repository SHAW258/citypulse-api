"""Create CityPulse's initial MySQL schema.

Revision ID: 20260814_0001
Revises:
Create Date: 2026-08-14 00:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260814_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

location_category = sa.Enum(
    "HOME",
    "WORK",
    "COLLEGE",
    "FOOD",
    "LEISURE",
    "SHOPPING",
    "HEALTH",
    "OTHER",
    name="locationcategory",
    native_enum=False,
    length=20,
)
transport_mode = sa.Enum(
    "WALK",
    "BIKE",
    "BUS",
    "TRAIN",
    "METRO",
    "CAR",
    "AUTO",
    "RIDE_SHARE",
    "OTHER",
    name="transportmode",
    native_enum=False,
    length=20,
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)

    op.create_table(
        "locations",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", location_category, nullable=False),
        sa.Column("latitude", sa.DECIMAL(precision=8, scale=6), nullable=True),
        sa.Column("longitude", sa.DECIMAL(precision=9, scale=6), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_locations_user_category", "locations", ["user_id", "category"], unique=False)

    op.create_table(
        "refresh_tokens",
        sa.Column("token_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("client_ip", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_id"),
    )
    op.create_index(op.f("ix_refresh_tokens_token_id"), "refresh_tokens", ["token_id"], unique=False)
    op.create_index("ix_refresh_tokens_user_active", "refresh_tokens", ["user_id", "revoked_at"], unique=False)

    op.create_table(
        "trips",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("origin_location_id", sa.String(length=36), nullable=True),
        sa.Column("destination_location_id", sa.String(length=36), nullable=True),
        sa.Column("transport_mode", transport_mode, nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=False),
        sa.Column("distance_km", sa.DECIMAL(precision=8, scale=2), nullable=False),
        sa.Column("cost", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("purpose", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("cost >= 0", name="ck_trips_cost_non_negative"),
        sa.CheckConstraint("distance_km >= 0", name="ck_trips_distance_non_negative"),
        sa.CheckConstraint("rating IS NULL OR rating BETWEEN 1 AND 5", name="ck_trips_rating_range"),
        sa.ForeignKeyConstraint(["destination_location_id"], ["locations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["origin_location_id"], ["locations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trips_user_started_at", "trips", ["user_id", "started_at"], unique=False)
    op.create_index("ix_trips_user_transport", "trips", ["user_id", "transport_mode"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_trips_user_transport", table_name="trips")
    op.drop_index("ix_trips_user_started_at", table_name="trips")
    op.drop_table("trips")
    op.drop_index("ix_refresh_tokens_user_active", table_name="refresh_tokens")
    op.drop_index(op.f("ix_refresh_tokens_token_id"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index("ix_locations_user_category", table_name="locations")
    op.drop_table("locations")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
