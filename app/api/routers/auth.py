from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.deps import get_current_user, get_user_by_email, create_user
from app.core.db import get_session
from app.core.security import create_access_token, verify_password
from app.models import User
from app.schemas.auth import Token
from app.schemas.users import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
async def register(
        user_in: UserCreate,
        session: AsyncSession = Depends(get_session),
):
    existing_email = await get_user_by_email(str(user_in.email), session)
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    stmt = select(User).where(User.username == user_in.username)
    existing_username = await session.scalar(stmt)
    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    user: User = await create_user(user_in=user_in, session=session)
    return user

@router.post("/login", response_model=Token)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_session),
):
    stmt = select(User).where(User.email == form_data.username)
    user: User | None = await session.scalar(stmt)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or password is invalid"
        )

    if not verify_password(
            plain_password=form_data.password,
            password_hash=user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or password is invalid"
        )

    access_token = create_access_token(user_id=user.id, role=user.role)
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserRead)
async def me(current_user = Depends(get_current_user)):
    return current_user