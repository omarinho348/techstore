from datetime import datetime, timezone
from enum import Enum

from beanie import Document
from pydantic import Field


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageLog(Document):

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    role: MessageRole

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:

        name = "message_logs"

        indexes = [
            "session_id",
            "created_at",
        ]