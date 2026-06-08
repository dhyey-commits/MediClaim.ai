"""
MediClaim AI — FastAPI Application Entry Point
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.database.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables + seed data. Shutdown: cleanup."""
    print("[MediClaim AI] API starting up...")
    try:
        await init_db()
        print("[OK] Database initialised")
    except Exception as e:
        print(f"[WARN] Database init warning: {e}")
    yield
    print("[MediClaim AI] API shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="MediClaim AI — Clinical Documentation Standardization Platform API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for static file serving
uploads_path = settings.upload_path
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# ── API Routes ───────────────────────────────────────────────────────────────
from app.api import health, claims, documents, reports, analytics  # noqa: E402

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(claims.router, prefix="/api/v1/claims", tags=["claims"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])


@app.get("/")
async def root() -> dict:
    return {
        "name": "MediClaim AI API",
        "version": settings.app_version,
        "status": "ok",
        "docs": "/docs",
    }
