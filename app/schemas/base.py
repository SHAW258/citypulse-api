"""Shared request-model defaults."""

from pydantic import BaseModel, ConfigDict


class StrictSchema(BaseModel):
    """Reject unknown request fields to prevent silent client mistakes."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ResponseSchema(BaseModel):
    """Enable safe conversion of SQLAlchemy objects into public responses."""

    model_config = ConfigDict(from_attributes=True)
