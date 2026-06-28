"""User registration, login, and lookup."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import AuthError, ConflictError
from app.models.orm import User
from app.security import create_access_token, hash_password, verify_password


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def _get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def register(
    db: AsyncSession, email: str, display_name: str, password: str
) -> User:
    if await _get_by_email(db, email) is not None:
        raise ConflictError("An account with this email already exists.")

    user = User(
        email=email,
        display_name=display_name,
        hashed_password=hash_password(password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, email: str, password: str) -> User:
    user = await _get_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise AuthError("Invalid email or password.")
    return user


def issue_token(user: User) -> str:
    return create_access_token(subject=str(user.id))
