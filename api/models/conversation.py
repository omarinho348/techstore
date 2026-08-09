from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class Conversation(Document):
    """
    Stores one chat conversation.
    """

    customer_id: str = Field(...)

    session_id: str = Field(...)

    title: str = Field(
        default="New Chat",
        max_length=200,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "conversations"

        indexes = [
            "customer_id",
            "session_id",
        ]