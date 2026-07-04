"""Shared FastAPI dependencies (auth)."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.manager import current_active_user
from app.db import get_db
from app.models.orm import User

CurrentUser = Annotated[User, Depends(current_active_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
