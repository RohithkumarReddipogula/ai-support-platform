from app.worker import celery_app


@celery_app.task(bind=True, max_retries=3, name="app.tasks.document_tasks.ingest_document")
def ingest_document(self, document_id: str, tenant_id: str):
    """
    Background task: chunk + embed + store a document.
    Expanded on Day 2 with full RAG pipeline.
    """
    try:
        # Day 2: add chunking, embedding, pgvector storage here
        print(f"Ingesting document {document_id} for tenant {tenant_id}")
        return {"status": "completed", "document_id": document_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
