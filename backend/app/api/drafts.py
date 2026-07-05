from typing import Annotated

from fastapi import APIRouter, Depends

from blog_ai_agent import BlogWriter

from app.ai import get_writer
from app.dependencies import CurrentUser, DbSession
from app.models.schemas import DraftCreate, DraftEdit, DraftPublic, DraftSaveFromRevision, PostPublic
from app.services import draft_service, post_service

router = APIRouter(prefix="/api/drafts", tags=["drafts"])

Writer = Annotated[BlogWriter, Depends(get_writer)]


@router.post("", response_model=DraftPublic, status_code=201)
async def create_draft(body: DraftCreate, user: CurrentUser, db: DbSession):
    return await draft_service.create(db, user, body)


@router.post("/from-revision", response_model=DraftPublic, status_code=201)
async def save_revision_as_draft(body: DraftSaveFromRevision, user: CurrentUser, db: DbSession):
    """Persist the final result of the 'revise my own draft' flow (see
    POST /api/revisions/stream) as an editable, publishable Draft."""
    return await draft_service.create_from_content(db, user, body)


@router.get("", response_model=list[DraftPublic])
async def list_drafts(user: CurrentUser, db: DbSession):
    return await draft_service.list_for_author(db, user)


@router.get("/{draft_id}", response_model=DraftPublic)
async def get_draft(draft_id: int, user: CurrentUser, db: DbSession):
    return await draft_service.get_owned(db, user, draft_id)


@router.post("/{draft_id}/generate", response_model=DraftPublic)
async def generate_draft(draft_id: int, user: CurrentUser, db: DbSession, writer: Writer):
    return await draft_service.generate(db, writer, user, draft_id)


@router.put("/{draft_id}", response_model=DraftPublic)
async def edit_draft(draft_id: int, body: DraftEdit, user: CurrentUser, db: DbSession):
    return await draft_service.edit(db, user, draft_id, body)


@router.post("/{draft_id}/publish", response_model=PostPublic, status_code=201)
async def publish_draft(draft_id: int, user: CurrentUser, db: DbSession):
    return await post_service.publish(db, user, draft_id)
