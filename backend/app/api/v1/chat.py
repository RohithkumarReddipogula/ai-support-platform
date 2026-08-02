import uuid
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.chat import Conversation, Message
from app.schemas.chat import ChatRequest, ChatResponse, SourceChunk, ConversationHistory, MessageOut
from app.core.auth import get_current_user
from app.services.rag import retrieve_relevant_chunks, build_context

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = str(current_user.tenant_id)
    session_id = request.session_id or str(uuid.uuid4())

    result = await db.execute(
        select(Conversation).where(
            Conversation.session_id == session_id,
            Conversation.tenant_id == current_user.tenant_id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        conversation = Conversation(
            tenant_id=current_user.tenant_id,
            session_id=session_id,
        )
        db.add(conversation)
        await db.flush()

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
        answer = "I don't have information about that in my knowledge base."

    user_msg = Message(
        conversation_id=conversation.id,
        tenant_id=current_user.tenant_id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)

    sources_json = json.dumps([
        {"content": c["content"][:200], "document_id": c["document_id"], "chunk_index": c["chunk_index"]}
        for c in chunks
    ])

    assistant_msg = Message(
        conversation_id=conversation.id,
        tenant_id=current_user.tenant_id,
        role="assistant",
        content=answer,
        sources=sources_json,
    )
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)

    sources = [
        SourceChunk(
            content=c["content"][:200],
            document_id=c["document_id"],
            chunk_index=c["chunk_index"],
        )
        for c in chunks
    ]

    return ChatResponse(
        answer=answer,
        session_id=session_id,
        sources=sources,
        message_id=assistant_msg.id,
    )


@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.session_id == session_id,
            Conversation.tenant_id == current_user.tenant_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    )
    messages = messages_result.scalars().all()
    return ConversationHistory(
        session_id=session_id,
        messages=[MessageOut.model_validate(m) for m in messages],
    )


@router.delete("/history/{session_id}")
async def clear_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import delete
    result = await db.execute(
        select(Conversation).where(
            Conversation.session_id == session_id,
            Conversation.tenant_id == current_user.tenant_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.execute(delete(Message).where(Message.conversation_id == conversation.id))
    await db.delete(conversation)
    await db.commit()
    return {"message": "Conversation cleared"}