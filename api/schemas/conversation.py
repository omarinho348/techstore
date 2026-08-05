from datetime import datetime

from pydantic import BaseModel


class ConversationResponse(BaseModel):
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime


class CreateConversationResponse(BaseModel):
    session_id: str
    title: str

class DeleteConversationResponse(BaseModel):
    session_id: str
    deleted: bool
    message: str    