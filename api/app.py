from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.auth import get_current_customer, hash_password, verify_password
from api.models.customer import Customer
from api.database import init_db, close_db
from api.routers.products import router as products_router
from api.routers.orders import router as orders_router
from api.routers.chat import router as chat_router
from api.routers.tickets import router as tickets_router
from api.routers.auth import router as auth_router
from api.routers.conversations import router as conversations_router
from api.routers.voice import router as voice_router
from api.schemas.auth import CustomerProfileResponse, UpdateProfileRequest
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    print("Starting TechStore Backend API...")

    await init_db()

    yield

    print("Shutting down TechStore Backend API...")

    await close_db()


app = FastAPI(
    title="TechStore Backend API",
    description="Backend API for the TechStore Agentic AI Chatbot",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/audio",
    StaticFiles(directory="audio"),
    name="audio",
)


app.include_router(products_router)
app.include_router(orders_router)
app.include_router(chat_router)
app.include_router(tickets_router)
app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(voice_router)

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """

    return {
        "status": "ok",
        "service": "TechStore Backend API",
    }

@app.get("/me", response_model=CustomerProfileResponse)
async def get_me(
    customer: Customer = Depends(
        get_current_customer
    ),
):
    return CustomerProfileResponse(
        customer_id=str(customer.id),
        name=customer.name,
        email=customer.email,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )


@app.patch("/me", response_model=CustomerProfileResponse)
async def update_me(
    request: UpdateProfileRequest,
    customer: Customer = Depends(
        get_current_customer
    ),
):
    if (
        request.name is None
        and request.email is None
        and request.new_password is None
    ):
        raise HTTPException(
            status_code=400,
            detail="At least one field must be provided.",
        )

    if request.email and request.email != customer.email:
        existing_customer = await Customer.find_one(
            Customer.email == request.email,
        )

        if existing_customer and existing_customer.id != customer.id:
            raise HTTPException(
                status_code=409,
                detail="A customer with this email already exists.",
            )

        customer.email = request.email

    if request.name is not None:
        customer.name = request.name

    if request.new_password is not None:
        if not request.current_password:
            raise HTTPException(
                status_code=400,
                detail="Current password is required to change your password.",
            )

        if not verify_password(
            request.current_password,
            customer.password_hash,
        ):
            raise HTTPException(
                status_code=401,
                detail="Current password is incorrect.",
            )

        customer.password_hash = hash_password(request.new_password)

    customer.updated_at = datetime.now(timezone.utc)

    await customer.save()

    return CustomerProfileResponse(
        customer_id=str(customer.id),
        name=customer.name,
        email=customer.email,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )