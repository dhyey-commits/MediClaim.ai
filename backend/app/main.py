"""
MediClaim AI — FastAPI Application Entry Point
Week 1 MVP: Upload Pipeline
"""

from __future__ import annotations

from contextlib import asynccontextmanager


from arq import create_pool
from app.worker import redis_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.logger import get_logger
logger = get_logger(__name__)

from app.core.config import get_settings
from app.database.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables + seed data. Shutdown: cleanup."""
    logger.info("[MediClaim AI] API starting up...")
    
    # Validate API Keys
    if not settings.gemini_api_key:
        logger.error("GEMINI_API_KEY is missing from environment variables.")
        raise ValueError("GEMINI_API_KEY is required to start the application.")
    else:
        logger.info("GEMINI_API_KEY loaded successfully")

    # Validate Auth Settings
    if not settings.auth_mock and not settings.clerk_issuer_url:
        logger.error("CLERK_ISSUER_URL is missing but AUTH_MOCK is false. Refusing to start in insecure state.")
        raise ValueError("CLERK_ISSUER_URL is required for production authentication.")

    try:
        app.state.redis = await create_pool(redis_settings)
        print("[OK] ARQ Redis Pool initialized")
    except Exception as e:
        if settings.environment.lower() == "production":
            logger.error("Failed to connect to Redis. Production mode requires Redis.")
            raise e
        else:
            logger.warning(f"Failed to connect to Redis. Running in local development mode without background jobs. Error: {e}")
            app.state.redis = None

    try:
        await init_db()
        logger.info("Database initialised")
    except Exception as e:
        logger.warning(f"Database init warning: {e}")

    # Ensure uploads directory exists
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload directory: {settings.upload_path}")

    yield

    if getattr(app.state, "redis", None):
        await app.state.redis.close()
    logger.info("[MediClaim AI] API shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="MediClaim AI — Clinical Documentation Standardization Platform API",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for static file serving
uploads_path = settings.upload_path
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# ── API Routes ───────────────────────────────────────────────────────────────
from app.api import health, claims, documents, reports, analytics, jobs, benchmarks

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(claims.router, prefix="/claims", tags=["claims"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(benchmarks.router, prefix="/api/v1/benchmarks")
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    with open("error.log", "w") as f:
        f.write(traceback.format_exc())
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.get("/")
async def root() -> dict:
    return {
        "name": "MediClaim AI API",
        "version": settings.app_version,
        "status": "ok",
        "docs": "/docs",
    }
