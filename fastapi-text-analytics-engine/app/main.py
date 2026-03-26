"""
FastAPI application factory and entry-point configuration.

Run locally with::

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router as analysis_router

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown hooks)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(application: FastAPI):
    """Runs on startup and shutdown."""
    logger.info("Text Analytics Engine is starting up …")
    yield
    logger.info("Text Analytics Engine is shutting down …")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Text Analytics Engine",
    description=(
        "A lightweight, high-performance REST API for text analysis.  "
        "Uses raw algorithmic implementations — hash-map frequency "
        "counting (O(N)) and min-heap Top-K extraction (O(N log K)) — "
        "with zero external NLP dependencies."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# -- CORS (permissive for demo; tighten in production) -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Routers -----------------------------------------------------------------
app.include_router(analysis_router)


# -- Health check ------------------------------------------------------------
@app.get("/health", tags=["Ops"], summary="Health check")
async def health_check() -> dict[str, str]:
    """Return a simple liveness probe response."""
    return {"status": "healthy"}
