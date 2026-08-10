from fastapi import APIRouter, Depends, HTTPException, status
from api.auth import get_current_customer
from api.models.customer import Customer

from api.models.product import Product
from api.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from tools import recommend_products


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


def product_to_response(product: Product) -> ProductResponse:
    """
    Convert a Beanie Product document into the API response schema.
    """

    return ProductResponse(
        id=str(product.id),
        name=product.name,
        description=product.description,
        price=product.price,
        category=product.category,
        stock=product.stock,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(product_data: ProductCreate):
    """
    Create a new product.
    """

    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category,
        stock=product_data.stock,
    )

    await product.insert()

    return product_to_response(product)


@router.get(
    "",
    response_model=list[ProductResponse],
)
async def list_products():
    """
    Return all products.
    """

    products = await Product.find_all().to_list()

    return [
        product_to_response(product)
        for product in products
    ]


@router.get("/recommendations")
async def get_recommendations(
    customer: Customer = Depends(get_current_customer),
):
    """Return personalized, in-stock product recommendations."""

    return await recommend_products(customer.email)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
async def get_product(product_id: str):
    """
    Return a single product by ID.
    """

    product = await Product.get(product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product_to_response(product)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
):
    """
    Update an existing product.
    """

    product = await Product.get(product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    update_data = product_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(product, field, value)

    await product.save()

    return product_to_response(product)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(product_id: str):
    """
    Delete an existing product.
    """

    product = await Product.get(product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    await product.delete()

    return None
