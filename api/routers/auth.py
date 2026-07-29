from fastapi import APIRouter, HTTPException

from api.auth import (
    create_access_token,
    hash_password,
    verify_password,
)
from api.models.customer import Customer
from api.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=AuthResponse,
)
async def register(
    request: RegisterRequest,
) -> AuthResponse:
    """
    Register a new customer.
    """

    existing_customer = await Customer.find_one(
        Customer.email == request.email,
    )

    if existing_customer:
        raise HTTPException(
            status_code=409,
            detail="A customer with this email already exists.",
        )

    customer = Customer(
        name=request.name,
        email=request.email,
        password_hash=hash_password(
            request.password,
        ),
    )

    await customer.insert()

    access_token = create_access_token(
        str(customer.id),
    )

    return AuthResponse(
        customer_id=str(customer.id),
        name=customer.name,
        email=customer.email,
        access_token=access_token,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
async def login(
    request: LoginRequest,
) -> AuthResponse:
    """
    Authenticate an existing customer.
    """

    customer = await Customer.find_one(
        Customer.email == request.email,
    )

    if not customer:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    if not verify_password(
        request.password,
        customer.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        str(customer.id),
    )

    return AuthResponse(
        customer_id=str(customer.id),
        name=customer.name,
        email=customer.email,
        access_token=access_token,
    )