import uuid

from fastapi import APIRouter

from fastapi import HTTPException

from api.models.message_log import MessageLog
from api.schemas.conversation import DeleteConversationResponse

from api.models.conversation import Conversation
from api.schemas.conversation import (
    ConversationResponse,
    CreateConversationResponse,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.get(
    "",
    response_model=list[ConversationResponse],
)
async def get_conversations():
    """
    Retrieve all conversations.
    Later this will return only the logged-in user's conversations.
    """

    conversations = (
        await Conversation.find_all()
        .sort(-Conversation.updated_at)
        .to_list()
    )

    return conversations


@router.post(
    "",
    response_model=CreateConversationResponse,
)
async def create_conversation():
    """
    Create a new conversation.
    """

    session_id = str(uuid.uuid4())

    conversation = Conversation(
        customer_id="TEMP_CUSTOMER",
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
):
    """
    Delete a conversation and all of its messages.
    """

    conversation = await Conversation.find_one(
        Conversation.session_id == session_id
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