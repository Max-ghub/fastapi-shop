from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import db
from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas.users import UserCreate, UserIn

INVALID_CREDENTIALS_DETAIL = "Email or password is invalid"
EMAIL_TAKEN_DETAIL = "Email already registered"
USERNAME_TAKEN_DETAIL = "Username already taken"


def raise_invalid_credentials() -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=INVALID_CREDENTIALS_DETAIL,
    )


async def ensure_email_unique(email: str, session: AsyncSession) -> None:
    stmt = select(User.id).where(User.email == email)
    if await db.exists(stmt, session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=EMAIL_TAKEN_DETAIL,
        )


async def ensure_username_unique(username: str, session: AsyncSession) -> None:
    stmt = select(User.id).where(User.username == username)
    if await db.exists(stmt, session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=USERNAME_TAKEN_DETAIL,
        )


async def ensure_user_credentials_unique(
    user: UserIn,
    session: AsyncSession,
) -> None:
    await ensure_email_unique(str(user.email), session)
    await ensure_username_unique(str(user.username), session)


def ensure_password_valid(plain_password: str, password_hash: str) -> None:
    if not verify_password(plain_password, password_hash):
        raise_invalid_credentials()


async def get_user_by_email(email: str, session: AsyncSession) -> User:
    stmt = select(User).where(User.email == email)
    user = await session.scalar(stmt)
    if user is None:
        raise_invalid_credentials()
    return user


async def create_user(
    user_create: UserCreate,
    session: AsyncSession,
) -> User:
    user = User(
        username=user_create.username,
        email=str(user_create.email),
        password_hash=get_password_hash(user_create.password),
        role="user",
    )
    await db.add(user, session)
    return user
