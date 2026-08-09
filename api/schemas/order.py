from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from api.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    """
    A product item submitted when creating an order.
    """

    product_id: str

    quantity: int = Field(
        ...,
        gt=0,
    )


class OrderItemResponse(BaseModel):
    """
    A product item returned as part of an order response.
    """

    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderCreate(BaseModel):
    """
    Request body for creating a new order.
    """

    customer_id: str

    items: list[OrderItemCreate] = Field(
        ...,
        min_length=1,
    )


class OrderStatusUpdate(BaseModel):
    """
    Request body for updating an order's status.
    """

    status: OrderStatus


class OrderResponse(BaseModel):
    """
    Response returned by the API for an order.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    customer_id: str
    items: list[OrderItemResponse]
    total: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime