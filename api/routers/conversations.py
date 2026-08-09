import uuid

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_customer
from api.models.conversation import Conversation
from api.models.customer import Customer
from api.models.message_log import MessageLog
from api.schemas.conversation import (
    ConversationResponse,
    CreateConversationResponse,
    DeleteConversationResponse,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.get(
    "",
    response_model=list[ConversationResponse],
)
async def get_conversations(
    current_customer: Customer = Depends(get_current_customer),
):
    """
    Retrieve only the logged-in customer's conversations.
    """

    conversations = (
        await Conversation.find(
            Conversation.customer_id == str(current_customer.id)
        )
        .sort(-Conversation.updated_at)
        .to_list()
    )

    return conversations


@router.post(
    "",
    response_model=CreateConversationResponse,
)
async def create_conversation(
    current_customer: Customer = Depends(get_current_customer),
):
    """
    Create a new conversation for the logged-in customer.
    """

    session_id = str(uuid.uuid4())

    conversation = Conversation(
        customer_id=str(current_customer.id),
        session_id=session_id,
        title="New Chat",
    )

    await conversation.insert()

    return CreateConversationResponse(
        session_id=session_id,
        title=conversation.title,
    )


@router.delete(
    "/{session_id}",
    response_model=DeleteConversationResponse,
)
async def delete_conversation(
    session_id: str,
    current_customer: Customer = Depends(get_current_customer),
):
    """
    Delete a conversation and all of its messages.
    """

    conversation = await Conversation.find_one(
        Conversation.session_id == session_id,
        Conversation.customer_id == str(current_customer.id),
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    await MessageLog.find(
        MessageLog.session_id == session_id
    ).delete()

    await conversation.delete()

    return DeleteConversationResponse(
        session_id=session_id,
        deleted=True,
        message="Conversation deleted successfully.",
    )