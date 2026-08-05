from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends

from api.auth import get_current_customer
from api.models.customer import Customer
from api.database import init_db, close_db
from api.routers.products import router as products_router
from api.routers.orders import router as orders_router
from api.routers.chat import router as chat_router
from api.routers.tickets import router as tickets_router
from api.routers.auth import router as auth_router
from api.routers.conversations import router as conversations_router
from api.routers.voice import router as voice_router
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

@app.get("/me")
async def get_me(
    customer: Customer = Depends(
        get_current_customer
    ),
):
    return {
        "id": str(customer.id),
        "name": customer.name,
        "email": customer.email,
    }