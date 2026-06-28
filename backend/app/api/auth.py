from fastapi import APIRouter

from app.dependencies import CurrentUser, DbSession
from app.models.schemas import TokenResponse, UserLogin, UserPublic, UserRegister
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: UserRegister, db: DbSession):
    user = await auth_service.register(
        db, email=body.email, display_name=body.display_name, password=body.password
    )
    return TokenResponse(access_token=auth_service.issue_token(user), user=user)


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin, db: DbSession):
    user = await auth_service.authenticate(db, email=body.email, password=body.password)
    return TokenResponse(access_token=auth_service.issue_token(user), user=user)


@router.get("/me", response_model=UserPublic)
async def me(user: CurrentUser):
    return user
