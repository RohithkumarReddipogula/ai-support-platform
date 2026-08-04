# AI Customer Support Platform

A production-grade, multi-tenant SaaS application that lets any business deploy an AI-powered customer support chatbot trained on their own documentation — built from scratch in 7 days as a solo project.

**Live Demo:** https://your-app.railway.app/docs  
**Widget Demo:** https://your-app.railway.app/static/demo.html  
**GitHub:** https://github.com/RohithkumarReddipogula/ai-support-platform

---

## What I Built

Businesses upload their support documents (FAQs, manuals, policies). The platform chunks and indexes them into PostgreSQL with pgvector. A embeddable JavaScript widget — added to any website with a single script tag — then answers customer questions in real time using a RAG pipeline backed by that knowledge base.

Every tenant gets a fully isolated knowledge base, their own API key, and a dedicated chat history. The same infrastructure that powers the dashboard also powers the public widget endpoint.

---

## Technical Architecture

```
Browser (React Dashboard)
        |
        v
FastAPI Backend ──────────────── PostgreSQL + pgvector
        |                               |
   JWT Auth                     Document chunks
        |                        Conversation history
   Document upload               User + tenant data
        |
   Chunking pipeline (sync)
        |
   pgvector full-text retrieval
        |
   Chat response with citations
        |
        v
Embeddable JS Widget (any website, one script tag)
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | FastAPI + Python 3.11 | Async-native, type-safe, OpenAPI docs auto-generated |
| Database | PostgreSQL 16 + pgvector | Relational + vector search in one system |
| Auth | JWT (access + refresh tokens) | Stateless, production-standard |
| Frontend | React + Vite + TailwindCSS | Fast builds, clean UI |
| Infrastructure | Docker Compose | Reproducible local and production environment |
| CI/CD | GitHub Actions | Automated test + build on every push |
| Monitoring | Prometheus /metrics + /health | Production observability |
| Deployment | Railway.app | Zero-config cloud deployment |

---

## Key Features

**Multi-tenant isolation** — Each business account gets its own knowledge base, API key, and conversation history. No data crosses tenant boundaries.

**Document ingestion pipeline** — Upload PDF, TXT, or DOCX. The platform extracts text, splits it into 400-word chunks, and stores them in PostgreSQL. Status tracking shows pending, processing, completed, or failed.

**RAG chat engine** — Incoming questions trigger a full-text search across the tenant's document chunks. Retrieved context is injected into the prompt and returned with source citations.

**Embeddable widget** — A standalone JavaScript file served from the backend. Any website can embed the support chat with one line:

```html
<script src="https://your-app.railway.app/static/widget.js" data-api-key="sk_xxx"></script>
```

**Public widget API** — A separate endpoint authenticates via tenant API key rather than JWT, so the widget works without a logged-in user session.

**Health monitoring** — `/health` returns live status of the database and Redis with uptime in seconds. `/metrics` exposes Prometheus-format data.

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /api/v1/auth/register | Public | Register user and create tenant |
| POST | /api/v1/auth/login | Public | Login, receive JWT tokens |
| POST | /api/v1/auth/refresh | Public | Refresh access token |
| GET | /api/v1/auth/me | JWT | Get current user and tenant |
| POST | /api/v1/documents/upload | JWT | Upload and process document |
| GET | /api/v1/documents | JWT | List tenant knowledge base |
| DELETE | /api/v1/documents/{id} | JWT | Remove document and chunks |
| POST | /api/v1/chat | JWT | RAG chat with source citations |
| GET | /api/v1/chat/history/{id} | JWT | Retrieve conversation history |
| POST | /api/v1/chat/widget | API Key | Public widget chat endpoint |
| GET | /health | Public | Database and Redis health check |
| GET | /metrics | Public | Prometheus metrics |

---

## Running Locally

```bash
git clone https://github.com/RohithkumarReddipogula/ai-support-platform
cd ai-support-platform
cp .env.example .env
# Add your GEMINI_API_KEY and a SECRET_KEY to .env
docker compose up --build
```

Visit `http://localhost:8000/docs` for the API, `http://localhost:5173` for the dashboard.

---

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

12 tests covering authentication, document upload, RAG chat, session continuity, and the public widget endpoint.

---

## Project Structure

```
ai-support-platform/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # auth, chat, documents, widget, health
│   │   ├── core/            # JWT security, auth dependencies
│   │   ├── models/          # SQLAlchemy models (User, Tenant, Document, Chat)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # RAG retrieval logic
│   │   └── static/          # widget.js + demo.html
│   ├── tests/               # pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/           # Login, Register, Dashboard
│       ├── components/      # ProtectedRoute
│       ├── hooks/           # useAuth context
│       └── services/        # Axios API client
├── docker-compose.yml
└── .github/workflows/ci.yml
```

---

## Build Log

| Day | What I built |
|---|---|
| Day 1 | FastAPI project setup, PostgreSQL + pgvector, JWT auth (register/login/refresh/me), Docker Compose, GitHub Actions CI |
| Day 2 | Document upload endpoint, text extraction, chunking pipeline, status tracking |
| Day 3 | RAG chat engine, conversation history, context injection, source citations |
| Day 4 | React dashboard — auth pages, document management, live chat UI |
| Day 5 | Embeddable JS widget, public widget API endpoint, demo page |
| Day 6 | pytest test suite (12 tests), Prometheus monitoring, health endpoint with uptime |
| Day 7 | Railway.app deployment, live public URL, demo data |

---

## Author

**Rohith Kumar Reddipogula**  
MSc Data Science — University of Europe for Applied Sciences, Potsdam (2026)  
Specialisation: NLP, RAG systems, ML engineering

[GitHub](https://github.com/RohithkumarReddipogula) | [LinkedIn](https://www.linkedin.com/in/rohith-kumar-reddipogula-a6692030b/) | [Portfolio](https://rohithkumarreddipogula.github.io) | [Live RAG Demo](https://rohith2026-hybrid-rag-demo.hf.space)
