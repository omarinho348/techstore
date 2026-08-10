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

    input_type: str = Field(default="text", max_length=20)

    audio_file: str | None = Field(default=None, max_length=500)

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


class TTSRequest(BaseModel):
    """
    Request body for converting a message to speech.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )


class TTSResponse(BaseModel):
    """
    Response returned after generating speech audio.
    """

    audio_url: str