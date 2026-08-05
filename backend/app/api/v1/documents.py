import uuid
import asyncio

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import get_db, AsyncSessionLocal
from app.models.user import User
from app.models.document import Document, DocumentChunk, DocumentStatus
from app.schemas.document import DocumentOut, DocumentList
from app.core.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {"pdf", "txt", "docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024


async def process_document_direct(document_id, tenant_id, content):
    import uuid as uuid_lib
    async with AsyncSessionLocal() as db:
        try:
            text_content = content.decode("utf-8", errors="ignore")
            words = text_content.split()
            chunks = []
            for i in range(0, len(words), 400):
                chunk = " ".join(words[i:i + 400])
                if chunk.strip():
                    chunks.append(chunk)
            for i, chunk in enumerate(chunks):
                chunk_obj = DocumentChunk(
                    id=uuid_lib.uuid4(),
                    document_id=document_id,
                    tenant_id=tenant_id,
                    content=chunk,
                    chunk_index=i,
                )
                db.add(chunk_obj)
            await db.execute(
                update(Document)
                .where(Document.id == document_id)
                .values(status=DocumentStatus.COMPLETED, chunk_count=len(chunks))
            )
            await db.commit()
            print(f"Processed {len(chunks)} chunks")
        except Exception as e:
            print(f"Error: {e}")
            await db.execute(
                update(Document)
                .where(Document.id == document_id)
                .values(status=DocumentStatus.FAILED, error_message=str(e))
            )
            await db.commit()


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"File type not supported.")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large.")
    document = Document(
        tenant_id=current_user.tenant_id,
        filename=file.filename,
        file_type=file_ext,
        status=DocumentStatus.PENDING,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    await process_document_direct(
        document_id=str(document.id),
        tenant_id=str(current_user.tenant_id),
        content=content,
    )
    await db.refresh(document)
    return document


@router.get("", response_model=DocumentList)
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document)
        .where(Document.tenant_id == current_user.tenant_id)
        .order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()
    return DocumentList(documents=documents, total=len(documents))


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == current_user.tenant_id
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import delete
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == current_user.tenant_id
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))
    await db.delete(document)
    await db.commit()