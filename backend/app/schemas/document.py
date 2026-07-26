import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.models.document import DocumentStatus


class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    file_type: str
    status: DocumentStatus
    chunk_count: int
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    documents: list[DocumentOut]
    total: int
