from datetime import datetime, timezone

from beanie import Document
from pydantic import EmailStr, Field


class Customer(Document):
    """
    Customer document stored in MongoDB.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    email: EmailStr

    password_hash: str = Field(
        ...,
        min_length=1,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "customers"

        indexes = [
            "email",
        ]