from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class Product(Document):
    """
    Product document stored in MongoDB.
    """

    name: str = Field(..., min_length=1, max_length=200)

    description: str = Field(
        default="",
        max_length=2000,
    )

    price: float = Field(
        ...,
        ge=0,
    )

    category: str = Field(
        default="",
        max_length=100,
    )

    stock: int = Field(
        default=0,
        ge=0,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "products"