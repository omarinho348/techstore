from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.database import init_db, close_db
from api.routers.products import router as products_router
from api.routers.orders import router as orders_router
from api.routers.chat import router as chat_router
from api.routers.tickets import router as tickets_router
from api.routers.auth import router as auth_router

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


app.include_router(products_router)
app.include_router(orders_router)
app.include_router(chat_router)
app.include_router(tickets_router)
app.include_router(auth_router)

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """

    return {
        "status": "ok",
        "service": "TechStore Backend API",
    }