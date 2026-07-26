-- Run this after docker compose up
-- Adds vector embedding column to document_chunks

ALTER TABLE document_chunks
ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- Index for fast similarity search per tenant
CREATE INDEX IF NOT EXISTS idx_chunks_tenant_embedding
ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
