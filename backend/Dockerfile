# syntax=docker/dockerfile:1
# Multi-stage build. The package is copied before app code so Docker layer
# caching is preserved (dependencies change rarely, app code changes often).

FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# Node.js + a Chromium install, needed to spawn the Playwright MCP server
# (`npx @playwright/mcp@latest`) that the researcher agent uses to read the
# author's linked sources during the revise flow.
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npx -y playwright install --with-deps chromium \
    && mkdir -p "$PLAYWRIGHT_BROWSERS_PATH" && chmod -R o+rX "$PLAYWRIGHT_BROWSERS_PATH"

# 1. Install the shared package first (changes rarely)
COPY packages/blog_ai_agent /packages/blog_ai_agent
RUN pip install /packages/blog_ai_agent

# 2. Install backend dependencies. Kept in sync by hand with
# backend/pyproject.toml's [project.dependencies] (app/ is copied *after*
# this step so dependency layers stay cached across app-code-only changes;
# installing via `pip install /app` here would need app/ present too early).
COPY backend/pyproject.toml /app/pyproject.toml
RUN pip install "fastapi>=0.110" "uvicorn[standard]>=0.29" "sqlalchemy[asyncio]>=2.0" \
    "asyncpg>=0.29" "pydantic>=2.7" "pydantic-settings>=2.2" \
    "fastapi-users[sqlalchemy]>=15.0" "python-multipart>=0.0.9"

# 3. Copy app code last (changes most often)
COPY backend/app /app/app

# Run as a non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
