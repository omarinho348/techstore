from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from api.models.customer import Customer
from api.models.order import Order, OrderItem, OrderStatus
from api.models.product import Product
from api.schemas.order import (
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
    OrderStatusUpdate,
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


def order_to_response(order: Order) -> OrderResponse:
    """
    Convert a Beanie Order document into the API response schema.
    """

    return OrderResponse(
        id=str(order.id),
        customer_id=order.customer_id,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in order.items
        ],
        total=order.total,
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(order_data: OrderCreate):
    """
    Create a new order.

    The client provides product IDs and quantities.
    Product names and prices are retrieved from MongoDB.

    The function validates the entire order before changing
    any product stock.
    """

    # ---------------------------------------------------------
    # 1. Verify that the customer exists
    # ---------------------------------------------------------

    customer = await Customer.get(order_data.customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    # ---------------------------------------------------------
    # 2. Validate all products and stock first
    # ---------------------------------------------------------

    order_items = []
    products_to_update = []
    total = 0.0

    for item_data in order_data.items:

        # Find the product
        product = await Product.get(item_data.product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item_data.product_id} not found",
            )

        # Check stock BEFORE modifying anything
        if product.stock < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock for product "
                    f"'{product.name}'. "
                    f"Available: {product.stock}, "
                    f"requested: {item_data.quantity}"
                ),
            )

        # Build the order item using current database values
        order_item = OrderItem(
            product_id=str(product.id),
            product_name=product.name,
            quantity=item_data.quantity,
            unit_price=product.price,
        )

        order_items.append(order_item)

        # Calculate total
        total += order_item.subtotal

        # Store the product for later stock update
        products_to_update.append(
            (product, item_data.quantity)
        )

    # ---------------------------------------------------------
    # 3. All validation passed
    # Now update product stock
    # ---------------------------------------------------------

    for product, quantity in products_to_update:

        product.stock -= quantity
        product.updated_at = datetime.now(timezone.utc)

        await product.save()

    # ---------------------------------------------------------
    # 4. Create the order
    # ---------------------------------------------------------

    order = Order(
        customer_id=str(customer.id),
        items=order_items,
        total=total,
        status=OrderStatus.PENDING,
    )

    # ---------------------------------------------------------
    # 5. Save the order
    # ---------------------------------------------------------

    await order.insert()

    # ---------------------------------------------------------
    # 6. Return the created order
    # ---------------------------------------------------------

    return order_to_response(order)


@router.get(
    "",
    response_model=list[OrderResponse],
)
async def list_orders():
    """
    Return all orders.
    """

    orders = await Order.find_all().to_list()

    return [
        order_to_response(order)
        for order in orders
    ]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
async def get_order(order_id: str):
    """
    Return a single order by ID.
    """

    order = await Order.get(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order_to_response(order)


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
)
async def update_order_status(
    order_id: str,
    status_data: OrderStatusUpdate,
):
    """
    Update the status of an existing order.
    """

    order = await Order.get(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    order.status = status_data.status
    order.updated_at = datetime.now(timezone.utc)

    await order.save()

    return order_to_response(order)