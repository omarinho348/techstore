from datetime import datetime, timezone
from enum import Enum

from beanie import Document
from pydantic import Field


class TicketStatus(str, Enum):
    """
    Possible states of a support ticket.
    """

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Ticket(Document):
    """
    Support ticket document stored in MongoDB.
    """

    ticket_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    customer_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    subject: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    description: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    status: TicketStatus = Field(
        default=TicketStatus.OPEN,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "tickets"