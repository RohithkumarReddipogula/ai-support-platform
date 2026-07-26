from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def retrieve_relevant_chunks(query, tenant_id, db, top_k=5):
    result = await db.execute(
        text("SELECT dc.id, dc.content, dc.document_id, dc.chunk_index, d.filename, 0.5 AS similarity FROM document_chunks dc JOIN documents d ON d.id = dc.document_id WHERE dc.tenant_id = :tenant_id ORDER BY dc.created_at DESC LIMIT :top_k"),
        {"tenant_id": tenant_id, "top_k": top_k}
    )
    rows = result.fetchall()
    return [{"id": str(r.id), "content": r.content, "document_id": str(r.document_id), "chunk_index": r.chunk_index, "filename": r.filename, "similarity": 0.5} for r in rows]


def build_context(chunks):
    if not chunks:
        return "No relevant information found."
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append("[Source " + str(i) + " - " + c["filename"] + "]\n" + c["content"])
    return "\n\n".join(parts)