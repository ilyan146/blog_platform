"""Publishing drafts into public posts, and reading published posts."""

import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import ConflictStateError, NotFoundError
from app.models.orm import Draft, DraftStatus, Post, User


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:140] or "post"


async def _unique_slug(db: AsyncSession, base: str) -> str:
    slug, n = base, 1
    while (
        await db.execute(select(Post.id).where(Post.slug == slug))
    ).scalar_one_or_none() is not None:
        n += 1
        slug = f"{base}-{n}"
    return slug


async def publish(db: AsyncSession, author: User, draft_id: int) -> Post:
    draft = await db.get(Draft, draft_id)
    if draft is None or draft.author_id != author.id:
        raise NotFoundError("Draft not found.")
    if draft.status is not DraftStatus.READY:
        raise ConflictStateError("Only a generated (ready) draft can be published.")

    # A draft maps to exactly one post (unique constraint); reject double-publish.
    existing = await db.execute(select(Post).where(Post.draft_id == draft.id))
    if existing.scalar_one_or_none() is not None:
        raise ConflictStateError("This draft has already been published.")

    post = Post(
        draft_id=draft.id,
        author_id=author.id,
        slug=await _unique_slug(db, _slugify(draft.title or "post")),
        title=draft.title or "Untitled",
        excerpt=draft.excerpt or "",
        body_markdown=draft.body_markdown or "",
        tags=draft.tags,
        reading_time_minutes=draft.reading_time_minutes or 1,
    )
    draft.status = DraftStatus.PUBLISHED
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def list_published(db: AsyncSession, limit: int = 50) -> list[Post]:
    result = await db.execute(
        select(Post).order_by(Post.published_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def get_by_slug(db: AsyncSession, slug: str) -> Post:
    result = await db.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if post is None:
        raise NotFoundError("Post not found.")
    return post
