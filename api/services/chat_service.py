"""
api/services/chat_service.py

Reusable chat pipeline.

Both the text endpoint and the future voice endpoint
call process_chat(), ensuring that voice and text
share exactly the same AI workflow.
"""

from datetime import datetime, timezone

from agents import Runner
from fastapi import HTTPException

from agent_team import triage_agent

from api.models.customer import Customer
from api.models.conversation import Conversation
from api.models.message_log import MessageLog, MessageRole
from api.schemas.chat import ChatResponse


def generate_title(message: str) -> str:
    """
    Generate a conversation title from the
    first customer message.
    """

    words = message.strip().split()

    if not words:
        return "New Chat"

    title = " ".join(words[:5])

    if len(words) > 5:
        title += "..."

    return title


async def process_chat(
    session_id: str,
    message: str,
    current_customer: Customer,
) -> ChatResponse:

    # ================================================================
    # LOAD CHAT HISTORY
    # ================================================================

    previous_messages = await MessageLog.find(
        MessageLog.session_id == session_id
    ).sort(
        MessageLog.created_at
    ).to_list()

    # ================================================================
    # CUSTOMER CONTEXT
    # ================================================================

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

Never ask the customer for their email.
"""

    # ================================================================
    # UPDATE CONVERSATION
    # ================================================================

    conversation = await Conversation.find_one(
        Conversation.session_id == session_id
    )

    if conversation:

        conversation.updated_at = datetime.now(timezone.utc)

        if (
            conversation.title == "New Chat"
            and len(previous_messages) == 0
        ):
            conversation.title = generate_title(message)

        await conversation.save()

    # ================================================================
    # BUILD AGENT INPUT
    # ================================================================

    input_items = [
        {
            "role": MessageRole.SYSTEM.value,
            "content": customer_context,
        }
    ]

    for previous in previous_messages:

        input_items.append(
            {
                "role": previous.role.value,
                "content": previous.message,
            }
        )

    input_items.append(
        {
            "role": MessageRole.USER.value,
            "content": message,
        }
    )

    # ================================================================
    # SAVE USER MESSAGE
    # ================================================================

    await MessageLog(
        session_id=session_id,
        role=MessageRole.USER,
        message=message,
    ).insert()

    # ================================================================
    # RUN AI
    # ================================================================

    result = await Runner.run(
        triage_agent,
        input=input_items,
    )

    if result.final_output is None:

        raise HTTPException(
            status_code=500,
            detail="The agent did not generate a response.",
        )

    assistant_response = str(result.final_output).strip()

    if not assistant_response:

        assistant_response = (
            "I'm sorry, I couldn't generate a response."
        )

    # ================================================================
    # SAVE AI RESPONSE
    # ================================================================

    assistant_message = MessageLog(
        session_id=session_id,
        role=MessageRole.ASSISTANT,
        message=assistant_response,
    )

    await assistant_message.insert()

    # ================================================================
    # RETURN
    # ================================================================

    return ChatResponse(
        session_id=session_id,
        response=assistant_response,
        created_at=assistant_message.created_at,
    )