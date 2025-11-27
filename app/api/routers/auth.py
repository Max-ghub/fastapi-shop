from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.depends import CurrentUserDep, SessionDep
from app.core.security import create_access_token
from app.models import User
from app.schemas.auth import Token
from app.schemas.users import UserCreate, UserIn, UserOut
from app.services.users import (
    create_user,
    ensure_password_valid,
    ensure_user_credentials_unique,
    get_user_by_email,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    path="/register", response_model=UserOut, status_code=status.HTTP_201_CREATED
)
async def register(user_create: UserCreate, session: SessionDep) -> User:
    user_in = UserIn(**user_create.model_dump())
    await ensure_user_credentials_unique(user_in, session)

    user = await create_user(user_create, session)
    return user


@router.post(path="/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    user = await get_user_by_email(form_data.username, session)
    ensure_password_valid(form_data.password, user.password_hash)

    access_token = create_access_token(user_id=user.id, role=user.role)
    return Token(access_token=access_token, token_type="bearer")


@router.get(path="/me", response_model=UserOut)
async def me(current_user: CurrentUserDep) -> User:
    return current_user
