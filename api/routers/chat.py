"""
api/routers/chat.py

Chat API endpoint for the TechStore Agentic AI Assistant.

This router:
- Receives customer messages through FastAPI.
- Loads conversation history from MongoDB.
- Saves user messages.
- Passes conversation history to the existing triage agent.
- Saves assistant responses.
- Returns the agent response.
- Provides an endpoint for retrieving conversation history.

The agentic AI logic remains in agent_team.py.
This router is responsible for the API and conversation persistence layer.
"""

from datetime import datetime, timezone

from agents import Runner
from fastapi import APIRouter, HTTPException
from fastapi import Depends

from api.auth import get_current_customer
from api.models.customer import Customer
from agent_team import triage_agent
from api.models.message_log import MessageLog, MessageRole
from api.schemas.chat import ChatRequest, ChatResponse
from api.models.conversation import Conversation


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

def generate_title(message: str) -> str:
    """
    Generate a short conversation title from the
    first user message.
    """

    words = message.strip().split()

    if not words:
        return "New Chat"

    title = " ".join(words[:5])

    if len(words) > 5:
        title += "..."

    return title

@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    current_customer: Customer = Depends(
        get_current_customer,
    ),
) -> ChatResponse:
    """
    Send a customer message to the TechStore agent team.

    Conversation history is loaded from MongoDB using session_id.
    The new user message and the assistant response are also persisted.
    """

    try:
        # ================================================================
        # 1. Load previous conversation history
        # ================================================================

        previous_messages = await MessageLog.find(
            MessageLog.session_id == request.session_id
        ).sort(
            MessageLog.created_at
        ).to_list()

        customer_context = f"""
You are TechStore's AI assistant.

The authenticated customer is:

Name: {current_customer.name}

Email: {current_customer.email}

Customer ID: {current_customer.id}

IMPORTANT

If you call get_my_orders,
ALWAYS use this email:

{current_customer.email}

Never ask the user for their email.
"""

        # ================================================================
        # Update conversation metadata
        # ================================================================

        conversation = await Conversation.find_one(
            Conversation.session_id == request.session_id
        )

        if conversation is not None:

            conversation.updated_at = datetime.now(timezone.utc)

        if (
            conversation.title == "New Chat"
            and len(previous_messages) == 0
        ):
            conversation.title = generate_title(
            request.message
        )

        await conversation.save()

        # ================================================================
        # 2. Build the Agents SDK input from conversation history
        # ================================================================

        input_items = []

        input_items.append(
        {
        "role": MessageRole.SYSTEM.value,
        "content": customer_context,
        }
        )

        for message in previous_messages:
            input_items.append(
        {
        "role": message.role.value,
        "content": message.message,
        }
        )
            input_items.append(
                {
                    "role": MessageRole.USER.value,
                    "content": request.message,
                }
            )

        # ================================================================
        # 3. Add the new user message to the agent input
        # ================================================================

        input_items.append(
            {
                "role": MessageRole.USER.value,
                "content": request.message,
            }
        )

        # ================================================================
        # 4. Save the new user message to MongoDB
        # ================================================================

        user_message = MessageLog(
            session_id=request.session_id,
            role=MessageRole.USER,
            message=request.message,
        )

        await user_message.insert()

        # ================================================================
        # 5. Run the existing TechStore agent team
        # ================================================================

        result = await Runner.run(
    triage_agent,
    input=input_items,
)

        # ================================================================
        # 6. Make sure the agent produced a response
        # ================================================================

        if result.final_output is None:
            raise HTTPException(
                status_code=500,
                detail="The agent did not generate a response.",
            )

        assistant_response = str(result.final_output)

        # ================================================================
        # 7. Save the assistant response to MongoDB
        # ================================================================

        assistant_message = MessageLog(
            session_id=request.session_id,
            role=MessageRole.ASSISTANT,
            message=assistant_response,
        )

        await assistant_message.insert()

        # ================================================================
        # 8. Return the API response
        # ================================================================

        return ChatResponse(
            session_id=request.session_id,
            response=assistant_response,
            created_at=assistant_message.created_at,
        )

    except HTTPException:
        raise

    except Exception as error:
        print(f"Chat processing error: {error}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your message.",
        ) from error


@router.get(
    "/{session_id}",
)
async def get_chat_history(session_id: str):
    """
    Retrieve all messages belonging to a conversation session.
    """

    try:
        messages = await MessageLog.find(
            MessageLog.session_id == session_id
        ).sort(
            MessageLog.created_at
        ).to_list()

        return {
            "session_id": session_id,
            "messages": [
                {
                    "role": message.role.value,
                    "message": message.message,
                    "created_at": message.created_at,
                }
                for message in messages
            ],
        }

    except Exception as error:
        print(f"Chat history error: {error}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving chat history.",
        ) from error


@router.delete(
    "/{session_id}",
)
async def delete_chat_history(session_id: str):
    """
    Delete all messages belonging to a chat session.
    """

    deleted_count = await MessageLog.find(
        MessageLog.session_id == session_id
    ).delete()

    return {
        "session_id": session_id,
        "deleted_count": deleted_count,
        "message": "Conversation history deleted successfully.",
    }