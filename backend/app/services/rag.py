from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.config import settings


async def embed_query(query: str) -> List[float]:
    """Embed a user query using Google Gemini embeddings."""
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)
    result = genai.embed_content(
        model="models/text-embedding-gecko-001",
        content=query,
        task_type="retrieval_query"
    )
    return result["embedding"]


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed multiple texts using Gemini."""
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)
    embeddings = []
    for text_item in texts:
        result = genai.embed_content(
            model="models/text-embedding-gecko-001",
            content=text_item,
            task_type="retrieval_document"
        )
        embeddings.append(result["embedding"])
    return embeddings


async def retrieve_relevant_chunks(
    query: str,
    tenant_id: str,
    db: AsyncSession,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """RAG retrieval using pgvector similarity search."""
    query_embedding = await embed_query(query)
    embedding_str = str(query_embedding)

    result = await db.execute(
        text("""
            SELECT
                dc.id,
                dc.content,
                dc.document_id,
                dc.chunk_index,
                d.filename,
                1 - (dc.embedding <=> :embedding::vector) AS similarity
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE dc.tenant_id = :tenant_id
              AND dc.embedding IS NOT NULL
            ORDER BY dc.embedding <=> :embedding::vector
            LIMIT :top_k
        """),
        {
            "embedding": embedding_str,
            "tenant_id": tenant_id,
            "top_k": top_k,
        }
    )

    rows = result.fetchall()
    return [
        {
            "id": str(row.id),
            "content": row.content,
            "document_id": str(row.document_id),
            "chunk_index": row.chunk_index,
            "filename": row.filename,
            "similarity": float(row.similarity),
        }
        for row in rows
    ]


def build_context(chunks: List[Dict[str, Any]]) -> str:
    """Format retrieved chunks into context string for LLM."""
    if not chunks:
        return "No relevant information found in the knowledge base."
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[Source {i} - {chunk['filename']}]\n{chunk['content']}")
    return "\n\n".join(context_parts)
