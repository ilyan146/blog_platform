"""SQLAlchemy ORM tables — the database row shapes (source of truth)."""

from __future__ import annotations

import enum
from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class DraftStatus(str, enum.Enum):
    """Lifecycle of an AI generation request attached to a draft."""

    PENDING = "pending"       # brief saved, generation not yet run
    GENERATING = "generating"  # agent is running
    READY = "ready"            # content generated, awaiting review/publish
    FAILED = "failed"          # generation errored
    PUBLISHED = "published"    # promoted to a Post


class User(SQLAlchemyBaseUserTable[int], Base):
    """Extends fastapi-users' base table (email, hashed_password, is_active,
    is_superuser, is_verified) with our own fields."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    drafts: Mapped[list[Draft]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )


class Draft(Base):
    """An author's brief plus the AI-generated content it produces."""

    __tablename__ = "drafts"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # --- The brief (input) ---
    topic: Mapped[str] = mapped_column(String(200))
    audience: Mapped[str] = mapped_column(String(200))
    tone: Mapped[str] = mapped_column(String(40))
    key_points: Mapped[list[str]] = mapped_column(JSON, default=list)

    # --- Generation state ---
    status: Mapped[DraftStatus] = mapped_column(
        Enum(DraftStatus, native_enum=False, length=20),
        default=DraftStatus.PENDING,
        index=True,
    )
    error: Mapped[str | None] = mapped_column(Text, default=None)

    # --- The generated content (output, null until READY) ---
    title: Mapped[str | None] = mapped_column(String(120), default=None)
    excerpt: Mapped[str | None] = mapped_column(String(320), default=None)
    body_markdown: Mapped[str | None] = mapped_column(Text, default=None)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    reading_time_minutes: Mapped[int | None] = mapped_column(default=None)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    author: Mapped[User] = relationship(back_populates="drafts")


class Post(Base):
    """A published, publicly readable blog post promoted from a Draft."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int] = mapped_column(
        ForeignKey("drafts.id", ondelete="CASCADE"), unique=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(120))
    excerpt: Mapped[str] = mapped_column(String(320))
    body_markdown: Mapped[str] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    reading_time_minutes: Mapped[int] = mapped_column()

    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    author: Mapped[User] = relationship()
