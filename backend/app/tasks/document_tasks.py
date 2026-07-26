import os
from typing import List

from celery import Task
from sqlalchemy import update

from app.worker import celery_app


def get_sync_db():
    """Synchronous DB session for Celery tasks."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.config import settings
    sync_url = getattr(settings, 'CELERY_DATABASE_URL', settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2"))
    engine = create_engine(sync_url)
    Session = sessionmaker(bind=engine)
    return Session()


def extract_text(file_path: str, file_type: str) -> str:
    if file_type == "txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif file_type == "pdf":
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        return "".join([page.extract_text() or "" for page in reader.pages])
    elif file_type == "docx":
        from docx import Document as DocxDocument
        doc = DocxDocument(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    return ""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        chunk = " ".join(words[start:start + chunk_size])
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


def get_embeddings(texts: List[str]) -> List[List[float]]:
    from openai import OpenAI
    from app.config import settings
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    embeddings = []
    for i in range(0, len(texts), 100):
        batch = texts[i:i + 100]
        response = client.embeddings.create(model="text-embedding-3-small", input=batch)
        embeddings.extend([item.embedding for item in response.data])
    return embeddings


@celery_app.task(bind=True, max_retries=3, name="app.tasks.document_tasks.ingest_document")
def ingest_document(self, document_id: str, tenant_id: str, file_path: str, file_type: str):
    from app.models.document import Document, DocumentStatus
    from sqlalchemy import text as sql_text
    import uuid

    db = get_sync_db()
    try:
        db.execute(update(Document).where(Document.id == document_id).values(status=DocumentStatus.PROCESSING))
        db.commit()

        text = extract_text(file_path, file_type)
        if not text.strip():
            raise ValueError("No text could be extracted from document")

        chunks = chunk_text(text)
        print(f"Created {len(chunks)} chunks")

        embeddings = get_embeddings(chunks)

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            db.execute(
                sql_text("""
                    INSERT INTO document_chunks (id, document_id, tenant_id, content, chunk_index, embedding, created_at)
                    VALUES (:id, :doc_id, :tenant_id, :content, :idx, :embedding, NOW())
                """),
                {"id": str(uuid.uuid4()), "doc_id": document_id, "tenant_id": tenant_id,
                 "content": chunk, "idx": i, "embedding": str(embedding)}
            )

        db.commit()
        db.execute(update(Document).where(Document.id == document_id).values(status=DocumentStatus.COMPLETED, chunk_count=len(chunks)))
        db.commit()
        print(f"Done: {len(chunks)} chunks stored")
        return {"status": "completed", "chunks": len(chunks)}

    except Exception as exc:
        db.execute(update(Document).where(Document.id == document_id).values(status=DocumentStatus.FAILED, error_message=str(exc)))
        db.commit()
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()
        if os.path.exists(file_path):
            os.remove(file_path)
