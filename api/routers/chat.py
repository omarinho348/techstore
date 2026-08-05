"""
api/routers/chat.py
"""

from datetime import datetime, timezone
import json

from agents import Runner
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from api.auth import get_current_customer
from api.models.conversation import Conversation
from api.models.customer import Customer
from api.models.message_log import MessageLog, MessageRole
from api.schemas.chat import ChatRequest, ChatResponse

from agent_team import triage_agent


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


def generate_title(message: str) -> str:

    words = message.strip().split()

    if not words:
        return "New Chat"

    title = " ".join(words[:5])

    if len(words) > 5:
        title += "..."

    return title


def build_customer_context(
    customer: Customer,
) -> str:

    return f"""
You are TechStore's AI assistant.

Authenticated customer:

Name: {customer.name}

Email: {customer.email}

Customer ID: {customer.id}

IMPORTANT:

If you call get_my_orders,
always use:

{customer.email}

Never ask the user for their email.
"""


async def load_history(
    session_id: str,
):

    return await MessageLog.find(
        MessageLog.session_id == session_id
    ).sort(
        MessageLog.created_at
    ).to_list()


async def update_conversation(
    session_id: str,
    first_message: str,
    previous_messages,
):

    conversation = await Conversation.find_one(
        Conversation.session_id == session_id
    )

    if conversation is None:
        return

    conversation.updated_at = datetime.now(
        timezone.utc,
    )

    if (
        conversation.title == "New Chat"
        and len(previous_messages) == 0
    ):
        conversation.title = generate_title(
            first_message,
        )

    await conversation.save()


def build_input_items(
    previous_messages,
    customer_context,
    new_message,
):

    items = [

        {
            "role": "system",
            "content": customer_context,
        }

    ]

    for message in previous_messages:

        items.append(

            {
                "role": message.role.value,
                "content": message.message,
            }

        )

    items.append(

        {
            "role": "user",
            "content": new_message,
        }

    )

    return items

@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    current_customer: Customer = Depends(
        get_current_customer,
    ),
):

    try:

        previous_messages = await load_history(
            request.session_id,
        )

        await update_conversation(
            request.session_id,
            request.message,
            previous_messages,
        )

        customer_context = build_customer_context(
            current_customer,
        )

        input_items = build_input_items(
            previous_messages,
            customer_context,
            request.message,
        )

        user_message = MessageLog(
            session_id=request.session_id,
            role=MessageRole.USER,
            message=request.message,
        )

        await user_message.insert()

        result = await Runner.run(
            triage_agent,
            input=input_items,
        )

        if result.final_output is None:

            raise HTTPException(
                status_code=500,
                detail="The agent did not generate a response.",
            )

        assistant_response = str(
            result.final_output,
        )

        assistant_message = MessageLog(
            session_id=request.session_id,
            role=MessageRole.ASSISTANT,
            message=assistant_response,
        )

        await assistant_message.insert()

        return ChatResponse(
            session_id=request.session_id,
            response=assistant_response,
            created_at=assistant_message.created_at,
        )

    except HTTPException:

        raise

    except Exception as error:

        print(
            "Chat processing error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail="Chat processing failed.",
        )

@router.post(
    "/stream",
)
async def stream_chat(
    request: ChatRequest,
    current_customer: Customer = Depends(
        get_current_customer,
    ),
):

    async def event_generator():

        previous_messages = await load_history(
            request.session_id,
        )

        await update_conversation(
            request.session_id,
            request.message,
            previous_messages,
        )

        customer_context = build_customer_context(
            current_customer,
        )

        input_items = build_input_items(
            previous_messages,
            customer_context,
            request.message,
        )

        user_message = MessageLog(
            session_id=request.session_id,
            role=MessageRole.USER,
            message=request.message,
        )

        await user_message.insert()

        result = Runner.run_streamed(
            triage_agent,
            input=input_items,
        )

        assistant_response = ""

        async for event in result.stream_events():

            event_name = type(event).__name__

            # ==========================================================
            # Agent changed
            # ==========================================================

            if event_name == "AgentUpdatedStreamEvent":

                yield (
                    "event: agent\n"
                    f"data: {json.dumps({'name': event.new_agent.name})}\n\n"
                )

            # ==========================================================
            # Tool calls / handoffs
            # ==========================================================

            elif event_name == "RunItemStreamEvent":

                item = event.item

                if hasattr(item, "raw_item"):

                    raw_item = item.raw_item

                    if hasattr(raw_item, "name"):

                        tool = raw_item.name

                        friendly = {

                            "transfer_to_order_and_product_agent":
                                "Routing to Order & Product Agent...",

                            "transfer_to_knowledge_agent":
                                "Routing to Knowledge Agent...",

                            "transfer_to_support_agent":
                                "Routing to Support Agent...",

                            "check_order_status":
                                "Checking your order...",

                            "get_my_orders":
                                "Retrieving your orders...",

                            "search_products":
                                "Searching products...",

                            "cancel_order":
                                "Cancelling your order...",

                            "check_refund_eligibility":
                                "Checking refund eligibility...",

                            "ticket_inquiry":
                                "Looking up your support ticket...",

                            "send_support_email":
                                "Sending support email...",

                            "search_knowledge_base":
                                "Searching our knowledge base...",

                        }.get(tool)

                        if friendly:

                            yield (
                                "event: status\n"
                                f"data: {json.dumps({'text': friendly})}\n\n"
                            )

            # ==========================================================
            # OpenAI streaming events
            # ==========================================================

            elif event_name == "RawResponsesStreamEvent":

                raw = event.data

                raw_name = type(raw).__name__

                # ------------------------------------------------------
                # Text token
                # ------------------------------------------------------

                if raw_name == "ResponseTextDeltaEvent":

                    assistant_response += raw.delta

                    yield (
                        "event: token\n"
                        f"data: {json.dumps({'text': raw.delta})}\n\n"
                    )

                # ------------------------------------------------------
                # Finished
                # ------------------------------------------------------

                elif raw_name == "ResponseCompletedEvent":

                    pass

        while not result.is_complete:

            await result.run_loop_task

        if not assistant_response and result.final_output is not None:

            assistant_response = str(
                result.final_output,
            )

        assistant_message = MessageLog(
            session_id=request.session_id,
            role=MessageRole.ASSISTANT,
            message=assistant_response,
        )

        await assistant_message.insert()

        yield (
            "event: done\n"
            "data: {}\n\n"
        )

        while not result.is_complete:

            await result.run_loop_task

        if result.final_output is not None:

            assistant_response = str(
                result.final_output,
            )

            assistant_message = MessageLog(
                session_id=request.session_id,
                role=MessageRole.ASSISTANT,
                message=assistant_response,
            )

            await assistant_message.insert()

            yield (
                f"event: final\n"
                f"data: {json.dumps({'response': assistant_response})}\n\n"
            )

        yield (
            "event: done\n"
            "data: {}\n\n"
        )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )

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