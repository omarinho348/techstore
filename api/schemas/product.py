from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    """
    Shared fields used by product requests and responses.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

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


class ProductCreate(ProductBase):
    """
    Request body for creating a new product.
    """

    pass


class ProductUpdate(BaseModel):
    """
    Request body for updating an existing product.

    All fields are optional so the client can update
    only the fields it wants to change.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    price: float | None = Field(
        default=None,
        ge=0,
    )

    category: str | None = Field(
        default=None,
        max_length=100,
    )

    stock: int | None = Field(
        default=None,
        ge=0,
    )


class ProductResponse(ProductBase):
    """
    Response returned by the API for a product.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    created_at: datetime
    updated_at: datetime