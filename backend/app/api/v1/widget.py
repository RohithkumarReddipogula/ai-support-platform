import uuid
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import Tenant
from app.models.chat import Conversation, Message
from app.services.rag import retrieve_relevant_chunks, build_context

router = APIRouter(prefix="/chat", tags=["widget"])


class WidgetChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    api_key: str


class WidgetChatResponse(BaseModel):
    answer: str
    session_id: str


@router.post("/widget", response_model=WidgetChatResponse)
async def widget_chat(request: WidgetChatRequest):
    """
    Public chat endpoint for the embeddable widget.
    Uses tenant API key instead of JWT — no login needed.
    """
    async with AsyncSessionLocal() as db:
        # Validate API key
        result = await db.execute(
            select(Tenant).where(
                Tenant.api_key == request.api_key,
                Tenant.is_active == True
            )
        )
        tenant = result.scalar_one_or_none()

        if not tenant:
            raise HTTPException(status_code=401, detail="Invalid API key")

        tenant_id = str(tenant.id)
        session_id = request.session_id or str(uuid.uuid4())

        # Get or create conversation
        result = await db.execute(
            select(Conversation).where(
                Conversation.session_id == session_id,
                Conversation.tenant_id == tenant.id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            conversation = Conversation(
                tenant_id=tenant.id,
                session_id=session_id,
            )
            db.add(conversation)
            await db.flush()

        # RAG retrieval
        chunks = await retrieve_relevant_chunks(
            query=request.message,
            tenant_id=tenant_id,
            db=db,
            top_k=5,
        )
        context = build_context(chunks)

        if chunks:
            answer = "Based on our knowledge base:\n\n" + context[:800]
        else:
            answer = "I don't have information about that in my knowledge base. Please contact our support team for help."

        # Save messages
        user_msg = Message(
            conversation_id=conversation.id,
            tenant_id=tenant.id,
            role="user",
            content=request.message,
        )
        db.add(user_msg)

        assistant_msg = Message(
            conversation_id=conversation.id,
            tenant_id=tenant.id,
            role="assistant",
            content=answer,
            sources=json.dumps([]),
        )
        db.add(assistant_msg)
        await db.commit()

        return WidgetChatResponse(answer=answer, session_id=session_id)
