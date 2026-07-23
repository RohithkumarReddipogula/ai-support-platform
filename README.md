# AI Customer Support Platform

A production-grade multi-tenant SaaS platform that lets businesses deploy an AI-powered
customer support chatbot trained on their own documentation — built on a RAG pipeline.

## What it does

- Businesses sign up and upload their support docs (FAQs, manuals, policies)
- The platform chunks, embeds, and indexes the documents using pgvector
- An embeddable chat widget appears on their website — powered by their own knowledge base
- Each tenant gets a fully isolated RAG pipeline with analytics

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Python 3.11 |
| Vector Database | PostgreSQL + pgvector |
| Background Jobs | Celery + Redis |
| RAG Engine | LangChain + OpenAI |
| Authentication | JWT (access + refresh tokens) |
| Frontend | React + Vite + TailwindCSS |
| Infrastructure | Docker Compose |
| CI/CD | GitHub Actions |
| Monitoring | Sentry + Prometheus |
| Deployment | Railway.app |

## Architecture

```
User Browser
    |
    v
React Dashboard -----> FastAPI Backend -----> PostgreSQL (users, tenants)
    |                       |                      |
    |                       |                 pgvector (embeddings)
    |                  Celery Worker
    |                       |
Chat Widget (embed) --------+-------------> Redis (job queue)
                            |
                         OpenAI API (LLM)
```

## Live Demo

- API Docs: [https://your-app.railway.app/docs]
- Demo Widget: [https://your-app.railway.app/demo]

## Quick Start

1. Clone the repo

```bash
git clone https://github.com/RohithkumarReddipogula/ai-support-platform
cd ai-support-platform
```

2. Copy environment file

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and a strong SECRET_KEY
```

3. Start all services

```bash
docker compose up --build
```

4. Visit API docs at http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/auth/register | Register new user + tenant |
| POST | /api/v1/auth/login | Login, receive JWT tokens |
| POST | /api/v1/auth/refresh | Refresh access token |
| GET | /api/v1/auth/me | Get current user profile |
| POST | /api/v1/documents/upload | Upload document to knowledge base |
| GET | /api/v1/documents | List tenant documents |
| POST | /api/v1/chat | Send message, receive RAG response |
| GET | /api/v1/analytics | Query stats and top questions |
| GET | /health | Health check (DB + Redis status) |
| GET | /metrics | Prometheus metrics |

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

## Build Progress

- [x] Day 1: Auth, PostgreSQL, Docker Compose, CI/CD
- [ ] Day 2: Document ingestion pipeline (Celery + pgvector)
- [ ] Day 3: RAG chat engine (LangChain + OpenAI streaming)
- [ ] Day 4: React dashboard
- [ ] Day 5: Embeddable chat widget
- [ ] Day 6: Monitoring + tests
- [ ] Day 7: Demo data + deployment

## Author

Rohith Kumar Reddipogula
[GitHub](https://github.com/RohithkumarReddipogula) |
[LinkedIn](https://www.linkedin.com/in/rohith-kumar-reddipogula-a6692030b/) |
[Portfolio](https://rohithkumarreddipogula.github.io)
