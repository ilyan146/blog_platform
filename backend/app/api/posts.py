from fastapi import APIRouter

from app.dependencies import DbSession
from app.models.schemas import PostPublic, PostSummary
from app.services import post_service

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("", response_model=list[PostSummary])
async def list_posts(db: DbSession):
    return await post_service.list_published(db)


@router.get("/{slug}", response_model=PostPublic)
async def get_post(slug: str, db: DbSession):
    return await post_service.get_by_slug(db, slug)
