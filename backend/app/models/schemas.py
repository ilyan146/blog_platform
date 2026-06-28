"""Pydantic schemas — the HTTP request/response contracts.

Kept separate from ORM models so the API surface and the database schema can
evolve independently.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.orm import DraftStatus

# --- Auth ---------------------------------------------------------------


class UserRegister(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    display_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


# --- Drafts -------------------------------------------------------------


class DraftCreate(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    audience: str = Field(default="a general technical audience", max_length=200)
    tone: str = "conversational"
    key_points: list[str] = Field(default_factory=list, max_length=10)


class DraftEdit(BaseModel):
    """Author tweaks to generated content before publishing."""

    title: str = Field(min_length=3, max_length=120)
    excerpt: str = Field(min_length=20, max_length=320)
    body_markdown: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list, max_length=6)


class DraftPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: DraftStatus
    error: str | None

    topic: str
    audience: str
    tone: str
    key_points: list[str]

    title: str | None
    excerpt: str | None
    body_markdown: str | None
    tags: list[str]
    reading_time_minutes: int | None

    created_at: datetime
    updated_at: datetime


# --- Posts --------------------------------------------------------------


class PostPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    excerpt: str
    body_markdown: str
    tags: list[str]
    reading_time_minutes: int
    published_at: datetime


class PostSummary(BaseModel):
    """Listing view — omits the full body to keep payloads small."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    excerpt: str
    tags: list[str]
    reading_time_minutes: int
    published_at: datetime
