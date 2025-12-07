from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import User
from app.repositories import UserRepository
from app.schemas.auth import Token
from app.schemas.users import UserCreate, UserIn, UserOut


def _ensure_password_valid(plain_password: str, password_hash: str) -> None:
    if not verify_password(plain_password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or password is invalid",
        )


class UserService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.session = db_session
        self.repo = UserRepository(db_session)

    async def _ensure_email_unique(self, email: str) -> None:
        stmt = select(select(User.id).where(User.email == email).exists())
        if await self.session.scalar(stmt):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    async def _ensure_username_unique(self, username: str) -> None:
        stmt = select(select(User.id).where(User.username == username).exists())
        if await self.session.scalar(stmt):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    async def _ensure_user_credentials_unique(self, user: UserIn) -> None:
        await self._ensure_email_unique(str(user.email))
        await self._ensure_username_unique(user.username)

    async def create_user(self, user: UserCreate) -> UserOut:
        await self._ensure_user_credentials_unique(user)
        user_db = User(
            username=user.username,
            email=str(user.email),
            password_hash=get_password_hash(user.password),
            role="user",
        )
        created_user = await self.repo.save(user_db)
        return UserOut.model_validate(created_user)

    async def authenticate_user(self, email: str, password: str) -> Token:
        user = await self.repo.get_user_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or password is invalid",
            )
        _ensure_password_valid(password, user.password_hash)
        access_token = create_access_token(user_id=user.id, role=user.role)
        return Token(access_token=access_token, token_type="bearer")
