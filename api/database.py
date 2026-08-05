import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from api.models import (
    Product,
    Order,
    Customer,
    Ticket,
    MessageLog,
    Conversation,
)


# Load variables from .env
load_dotenv()


# Read MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")


# Validate environment variables
if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not set in the .env file")

if not MONGODB_DATABASE:
    raise ValueError("MONGODB_DATABASE is not set in the .env file")


# Create MongoDB client
client = AsyncIOMotorClient(MONGODB_URI)


# Select database
database = client[MONGODB_DATABASE]


async def init_db():
    """
    Connect to MongoDB Atlas and initialize Beanie.
    """

    # Test the MongoDB connection
    await client.admin.command("ping")

    print("Successfully connected to MongoDB Atlas.")
    print(f"MongoDB database: {MONGODB_DATABASE}")

    # Initialize Beanie with all database document models
    await init_beanie(
        database=database,
        document_models=[
            Product,
            Order,
            Customer,
            Ticket,
            MessageLog,
            Conversation,
        ],
    )

    print("Beanie initialized successfully.")


async def close_db():
    """
    Close the MongoDB connection.
    """

    client.close()

    print("MongoDB connection closed.")