"""
api/routers/chat.py
"""

from datetime import datetime, timezone
import os
import json

from agents import Runner
from fastapi import UploadFile, File, Form

from PIL import Image
import pytesseract
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from agent_team import triage_agent

from api.auth import get_current_customer
from api.models.conversation import Conversation
from api.models.customer import Customer
from api.models.message_log import MessageLog, MessageRole
from api.schemas.chat import ChatRequest, ChatResponse


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


def build_customer_context(customer: Customer) -> str:
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


async def get_owned_conversation(
    session_id: str,
    current_customer: Customer,
):
    return await Conversation.find_one(
        Conversation.session_id == session_id,
        Conversation.customer_id == str(current_customer.id),
    )


async def load_history(session_id: str):
    return await MessageLog.find(
        MessageLog.session_id == session_id,
    ).sort(
        MessageLog.created_at,
    ).to_list()


async def update_conversation(
    conversation: Conversation,
    first_message: str,
    previous_messages,
):
    conversation.updated_at = datetime.now(timezone.utc)

    if conversation.title == "New Chat" and len(previous_messages) == 0:
        conversation.title = generate_title(first_message)

    await conversation.save()


def build_input_items(
    previous_messages,
    customer_context: str,
    new_message: str,
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
    current_customer: Customer = Depends(get_current_customer),
):
    try:
        conversation = await get_owned_conversation(
            request.session_id,
            current_customer,
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        previous_messages = await load_history(request.session_id)

        await update_conversation(
            conversation,
            request.message,
            previous_messages,
        )

        customer_context = build_customer_context(current_customer)

        input_items = build_input_items(
            previous_messages,
            customer_context,
            request.message,
        )

        await MessageLog(
            session_id=request.session_id,
            role=MessageRole.USER,
            message=request.message,
        ).insert()

        result = await Runner.run(
            triage_agent,
            input=input_items,
        )

        if result.final_output is None:
            raise HTTPException(
                status_code=500,
                detail="The agent did not generate a response.",
            )

        assistant_response = str(result.final_output)

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
        print("Chat processing error:", error)

        raise HTTPException(
            status_code=500,
            detail="Chat processing failed.",
        ) from error


@router.post(
    "/stream",
)
async def stream_chat(
    request: ChatRequest,
    current_customer: Customer = Depends(get_current_customer),
):
    async def event_generator():
        conversation = await get_owned_conversation(
            request.session_id,
            current_customer,
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        previous_messages = await load_history(request.session_id)

        await update_conversation(
            conversation,
            request.message,
            previous_messages,
        )

        customer_context = build_customer_context(current_customer)

        input_items = build_input_items(
            previous_messages,
            customer_context,
            request.message,
        )

        await MessageLog(
            session_id=request.session_id,
            role=MessageRole.USER,
            message=request.message,
        ).insert()

        result = Runner.run_streamed(
            triage_agent,
            input=input_items,
        )

        assistant_response = ""

        async for event in result.stream_events():
            event_name = type(event).__name__

            if event_name == "AgentUpdatedStreamEvent":
                yield (
                    "event: agent\n"
                    f"data: {json.dumps({'name': event.new_agent.name})}\n\n"
                )

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

            elif event_name == "RawResponsesStreamEvent":
                raw = event.data
                raw_name = type(raw).__name__

                if raw_name == "ResponseTextDeltaEvent":
                    assistant_response += raw.delta

                    yield (
                        "event: token\n"
                        f"data: {json.dumps({'text': raw.delta})}\n\n"
                    )

        while not result.is_complete:
            await result.run_loop_task

        if not assistant_response:
            if result.final_output is not None:
                assistant_response = str(result.final_output)

        # Ensure we never insert an empty message (pydantic enforces min_length=1)
        if not assistant_response or assistant_response.strip() == "":
            assistant_response = "[No response generated by the assistant]"

        await MessageLog(
            session_id=request.session_id,
            role=MessageRole.ASSISTANT,
            message=assistant_response,
        ).insert()

        yield (
            "event: final\n"
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



@router.post(
    "/upload",
)
async def upload_image_and_chat(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    current_customer: Customer = Depends(get_current_customer),
):
    """
    Accept an image upload, extract text via OCR, then process the
    extracted text through the same agent workflow as a normal chat
    message. Returns a ChatResponse.
    """
    try:
        conversation = await get_owned_conversation(
            session_id,
            current_customer,
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        # Save uploaded file to uploads/ with a safe name
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        filename = f"{session_id}-{int(datetime.now(timezone.utc).timestamp())}-{file.filename}"
        file_path = os.path.join(uploads_dir, filename)

        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        # Attempt OCR
        try:
            image = Image.open(file_path)
            extracted = pytesseract.image_to_string(image)
        except Exception as ocr_err:
            logger.error("OCR failed: %s", ocr_err)
            extracted = ""

        message_text = extracted.strip()

        if not message_text:
            message_text = "[Image uploaded but no text was detected]"

        previous_messages = await load_history(session_id)

        await update_conversation(
            conversation,
            message_text,
            previous_messages,
        )

        customer_context = build_customer_context(current_customer)

        input_items = build_input_items(
            previous_messages,
            customer_context,
            message_text,
        )

        await MessageLog(
            session_id=session_id,
            role=MessageRole.USER,
            message=message_text,
        ).insert()

        result = await Runner.run(
            triage_agent,
            input=input_items,
        )

        if result.final_output is None:
            raise HTTPException(
                status_code=500,
                detail="The agent did not generate a response.",
            )

        assistant_response = str(result.final_output)

        assistant_message = MessageLog(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            message=assistant_response or "[No response generated by the assistant]",
        )

        await assistant_message.insert()

        return ChatResponse(
            session_id=session_id,
            response=assistant_response,
            created_at=assistant_message.created_at,
        )

    except HTTPException:
        raise

    except Exception as error:
        print("Image chat processing error:", error)

        raise HTTPException(
            status_code=500,
            detail="Image chat processing failed.",
        ) from error


@router.get(
    "/{session_id}",
)
async def get_chat_history(
    session_id: str,
    current_customer: Customer = Depends(get_current_customer),
):
    """
    Retrieve all messages belonging to a conversation session.
    """

    try:
        conversation = await get_owned_conversation(
            session_id,
            current_customer,
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        messages = await MessageLog.find(
            MessageLog.session_id == session_id,
        ).sort(
            MessageLog.created_at,
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

    except HTTPException:
        raise

    except Exception as error:
        print(f"Chat history error: {error}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving chat history.",
        ) from error


@router.delete(
    "/{session_id}",
)
async def delete_chat_history(
    session_id: str,
    current_customer: Customer = Depends(get_current_customer),
):
    """
    Delete all messages belonging to a chat session.
    """

    conversation = await get_owned_conversation(
        session_id,
        current_customer,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    deleted_count = await MessageLog.find(
        MessageLog.session_id == session_id,
    ).delete()

    await conversation.delete()

    return {
        "session_id": session_id,
        "deleted_count": deleted_count,
        "message": "Conversation history deleted successfully.",
    }