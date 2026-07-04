"""User registration, login, and lookup — delegates to fastapi-users."""

from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions

from app.auth.manager import UserCreate, UserManager, get_jwt_strategy
from app.errors import AuthError, ConflictError
from app.models.orm import User


async def register(
    manager: UserManager, email: str, display_name: str, password: str
) -> User:
    try:
        return await manager.create(
            UserCreate(email=email, password=password, display_name=display_name)
        )
    except exceptions.UserAlreadyExists as exc:
        raise ConflictError("An account with this email already exists.") from exc


async def authenticate(manager: UserManager, email: str, password: str) -> User:
    credentials = OAuth2PasswordRequestForm(username=email, password=password)
    user = await manager.authenticate(credentials)
    if user is None:
        raise AuthError("Invalid email or password.")
    return user


async def issue_token(user: User) -> str:
    return await get_jwt_strategy().write_token(user)
