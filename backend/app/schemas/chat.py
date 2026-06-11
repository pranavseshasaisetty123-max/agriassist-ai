from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.chat import SenderRole


class ChatMessageBase(BaseModel):
    sender: SenderRole
    message_text: str = Field(..., min_length=1)


class ChatMessageCreate(BaseModel):
    message_text: str = Field(..., min_length=1)


class ChatMessageResponse(ChatMessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class ChatSessionCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)


class ChatSessionResponse(ChatSessionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    user_message: ChatMessageResponse
    ai_response: ChatMessageResponse
