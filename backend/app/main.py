"""Application entrypoint: wires middleware, error handling, and routers."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, drafts, posts
from app.config import settings
from app.db import init_db
from app.errors import AppError
from app.middleware.logging import LoggingMiddleware

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # create missing tables on boot
    yield


app = FastAPI(title="AI Blog Platform", version="0.1.0", lifespan=lifespan)

# CORS first so browser preflight (OPTIONS) is handled before anything else.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)


@app.exception_handler(AppError)
async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    """Map domain errors to clean JSON responses (services stay HTTP-free)."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(auth.router)
app.include_router(drafts.router)
app.include_router(posts.router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
