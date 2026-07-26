from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.database import create_tables
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.documents import router as documents_router
from app.models import document  # ensure tables are created


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print(f"Starting {settings.APP_NAME}...")
    await create_tables()
    print("Database tables created.")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-tenant AI Customer Support Platform powered by RAG",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app)

# Sentry (enabled in production)
if settings.SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=settings.APP_ENV,
    )

# Routers
app.include_router(health_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
