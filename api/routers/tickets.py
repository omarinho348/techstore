from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from api.models.ticket import Ticket, TicketStatus


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


class TicketCreate(BaseModel):
    """
    Request body for creating a support ticket.
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


class TicketStatusUpdate(BaseModel):
    """
    Request body for updating a ticket status.
    """

    status: TicketStatus


@router.post(
    "",
    response_model=Ticket,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket(ticket_data: TicketCreate):
    """
    Create a new support ticket.
    """

    existing_ticket = await Ticket.find_one(
        Ticket.ticket_id == ticket_data.ticket_id
    )

    if existing_ticket:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Ticket with ID "
                f"{ticket_data.ticket_id} already exists"
            ),
        )

    now = datetime.now(timezone.utc)

    ticket = Ticket(
        ticket_id=ticket_data.ticket_id.strip().upper(),
        customer_id=ticket_data.customer_id,
        subject=ticket_data.subject,
        description=ticket_data.description,
        status=TicketStatus.OPEN,
        created_at=now,
        updated_at=now,
    )

    await ticket.insert()

    return ticket


@router.get(
    "",
    response_model=list[Ticket],
)
async def list_tickets():
    """
    Return all support tickets.
    """

    return await Ticket.find_all().to_list()


@router.get(
    "/{ticket_id}",
    response_model=Ticket,
)
async def get_ticket(ticket_id: str):
    """
    Get a support ticket by its human-readable ticket ID.
    """

    normalized_ticket_id = ticket_id.strip().upper()

    ticket = await Ticket.find_one(
        Ticket.ticket_id == normalized_ticket_id
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Ticket with ID "
                f"{normalized_ticket_id} not found"
            ),
        )

    return ticket


@router.patch(
    "/{ticket_id}/status",
    response_model=Ticket,
)
async def update_ticket_status(
    ticket_id: str,
    status_data: TicketStatusUpdate,
):
    """
    Update the status of a support ticket.
    """

    normalized_ticket_id = ticket_id.strip().upper()

    ticket = await Ticket.find_one(
        Ticket.ticket_id == normalized_ticket_id
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Ticket with ID "
                f"{normalized_ticket_id} not found"
            ),
        )

    ticket.status = status_data.status
    ticket.updated_at = datetime.now(timezone.utc)

    await ticket.save()

    return ticket


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_ticket(ticket_id: str):
    """
    Delete a support ticket.
    """

    normalized_ticket_id = ticket_id.strip().upper()

    ticket = await Ticket.find_one(
        Ticket.ticket_id == normalized_ticket_id
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Ticket with ID "
                f"{normalized_ticket_id} not found"
            ),
        )

    await ticket.delete()

    return None