"""fastapi-users wiring: user DB adapter, manager, JWT auth backend.

This is the only place that talks to the fastapi-users library directly —
services/auth_service.py and api/auth.py depend on the small surface exposed
here (`UserManager`, `get_user_manager`, `get_jwt_strategy`,
`current_active_user`), not on fastapi-users itself.
"""

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin, schemas
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models.orm import User


class UserCreate(schemas.BaseUserCreate):
    """Adds our custom field on top of fastapi-users' email/password base."""

    display_name: str


async def get_user_db(db: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(db, User)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.jwt_secret
    verification_token_secret = settings.jwt_secret


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="api/auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.jwt_secret,
        lifetime_seconds=settings.access_token_ttl_minutes * 60,
        algorithm=settings.jwt_algorithm,
    )


auth_backend = AuthenticationBackend(
    name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)
