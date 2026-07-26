import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # If None, starts a new conversation


class SourceChunk(BaseModel):
    content: str
    document_id: str
    chunk_index: int


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: List[SourceChunk]
    message_id: uuid.UUID


class MessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationHistory(BaseModel):
    session_id: str
    messages: List[MessageOut]
