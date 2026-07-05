"""Test fixtures: in-memory SQLite DB and a fake AI writer.

Proves the services/API are testable without Postgres or Azure.
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://example.test")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from blog_ai_agent import BlogBrief, BlogDraft, RevisionBrief, ResearchNotes

from app.ai import get_researcher, get_writer
from app.db import get_db
from app.main import app
from app.models.orm import Base


class FakeResearcher:
    """Returns deterministic notes — no subprocess, no browser."""

    async def research(self, brief: RevisionBrief, *, on_progress=None) -> ResearchNotes:
        return ResearchNotes(summary="Fake research summary.", sources=list(brief.links))


class FakeWriter:
    """Returns a deterministic draft — no network, no Azure."""

    async def revise(self, brief: RevisionBrief, notes: ResearchNotes, *, on_progress=None) -> BlogDraft:
        body = " ".join(["word"] * 1100)
        return BlogDraft(
            title="Revised draft",
            excerpt="A concise, deterministic excerpt for testing purposes.",
            body_markdown=body,
            tags=["revised"],
        )

    async def write(self, brief: BlogBrief) -> BlogDraft:
        body = " ".join(["word"] * 1100)
        return BlogDraft(
            title=f"On {brief.topic}",
            excerpt="A concise, deterministic excerpt for testing purposes.",
            body_markdown=body,
            tags=["test"],
        )


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async def override_db():
        async with Session() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_writer] = lambda: FakeWriter()
    app.dependency_overrides[get_researcher] = lambda: FakeResearcher()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    await engine.dispose()
