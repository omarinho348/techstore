from datetime import datetime, timezone
from enum import Enum

from beanie import Document
from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    """
    Possible states of an order.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    """
    A single product inside an order.
    """

    product_id: str

    product_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    quantity: int = Field(
        ...,
        gt=0,
    )

    unit_price: float = Field(
        ...,
        ge=0,
    )

    @property
    def subtotal(self) -> float:
        """
        Calculate the subtotal for this item.
        """

        return self.quantity * self.unit_price


class Order(Document):
    """
    Order document stored in MongoDB.
    """

    customer_id: str

    items: list[OrderItem] = Field(
        ...,
        min_length=1,
    )

    total: float = Field(
        ...,
        ge=0,
    )

    status: OrderStatus = Field(
        default=OrderStatus.PENDING,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "orders"