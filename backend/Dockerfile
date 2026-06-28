# syntax=docker/dockerfile:1
# Multi-stage build. The package is copied before app code so Docker layer
# caching is preserved (dependencies change rarely, app code changes often).

FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# 1. Install the shared package first (changes rarely)
COPY packages/blog_ai_agent /packages/blog_ai_agent
RUN pip install /packages/blog_ai_agent

# 2. Install backend dependencies
COPY backend/pyproject.toml /app/pyproject.toml
RUN pip install fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" asyncpg \
    pydantic pydantic-settings "python-jose[cryptography]" bcrypt \
    python-multipart

# 3. Copy app code last (changes most often)
COPY backend/app /app/app

# Run as a non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
