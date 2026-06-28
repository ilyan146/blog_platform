"""Draft lifecycle: create brief, run AI generation, edit generated content."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from blog_ai_agent import BlogBrief, BlogGenerationError, BlogTone, BlogWriter

from app.errors import ConflictStateError, NotFoundError
from app.models.orm import Draft, DraftStatus, User


async def create(db: AsyncSession, author: User, data) -> Draft:
    draft = Draft(
        author_id=author.id,
        topic=data.topic,
        audience=data.audience,
        tone=data.tone,
        key_points=data.key_points,
        status=DraftStatus.PENDING,
    )
    db.add(draft)
    await db.commit()
    await db.refresh(draft)
    return draft


async def list_for_author(db: AsyncSession, author: User) -> list[Draft]:
    result = await db.execute(
        select(Draft)
        .where(Draft.author_id == author.id)
        .order_by(Draft.created_at.desc())
    )
    return list(result.scalars().all())


async def get_owned(db: AsyncSession, author: User, draft_id: int) -> Draft:
    draft = await db.get(Draft, draft_id)
    if draft is None or draft.author_id != author.id:
        raise NotFoundError("Draft not found.")
    return draft


async def generate(
    db: AsyncSession, writer: BlogWriter, author: User, draft_id: int
) -> Draft:
    """Run the AI agent for a draft and persist the result.

    Generation is allowed from PENDING, FAILED, or READY (regenerate). A
    PUBLISHED draft is locked.
    """
    draft = await get_owned(db, author, draft_id)
    if draft.status is DraftStatus.PUBLISHED:
        raise ConflictStateError("Cannot regenerate a published draft.")

    draft.status = DraftStatus.GENERATING
    draft.error = None
    await db.commit()

    brief = BlogBrief(
        topic=draft.topic,
        audience=draft.audience,
        tone=BlogTone(draft.tone),
        key_points=draft.key_points,
    )

    try:
        result = await writer.write(brief)
    except BlogGenerationError as exc:
        draft.status = DraftStatus.FAILED
        draft.error = str(exc)
        await db.commit()
        await db.refresh(draft)
        return draft

    draft.title = result.title
    draft.excerpt = result.excerpt
    draft.body_markdown = result.body_markdown
    draft.tags = result.tags
    draft.reading_time_minutes = result.reading_time_minutes
    draft.status = DraftStatus.READY
    await db.commit()
    await db.refresh(draft)
    return draft


async def edit(db: AsyncSession, author: User, draft_id: int, data) -> Draft:
    """Author edits the generated content before publishing."""
    draft = await get_owned(db, author, draft_id)
    if draft.status not in (DraftStatus.READY, DraftStatus.PUBLISHED):
        raise ConflictStateError("Only generated drafts can be edited.")

    draft.title = data.title
    draft.excerpt = data.excerpt
    draft.body_markdown = data.body_markdown
    draft.tags = data.tags
    draft.reading_time_minutes = max(1, round(len(data.body_markdown.split()) / 225))
    await db.commit()
    await db.refresh(draft)
    return draft
