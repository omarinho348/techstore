from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request body for sending a message to the chatbot.
    """

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )


class ChatResponse(BaseModel):
    """
    Response returned by the chatbot API.
    """

    session_id: str

    response: str

    created_at: datetime