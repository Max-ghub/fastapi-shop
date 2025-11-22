from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.db import get_session
from app.core.security import get_password_hash, decode_access_token
from app.models import User
from app.schemas.auth import TokenData
from app.schemas.users import UserCreate


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_user_by_email(
        email: str,
        session: AsyncSession = Depends(get_session)
) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await session.scalar(stmt)
    return result

async def create_user(
        user_in: UserCreate,
        session: AsyncSession = Depends(get_session)
) -> User:
    user_db = User(
        username=user_in.username,
        email = str(user_in.email),
        password_hash=get_password_hash(user_in.password),
        role="user"
    )
    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)
    return user_db


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token=token)
    except JWTError:
        raise credentials_exception

    token_data = TokenData(
        user_id=payload.get("user_id"),
        role=payload.get("role"),
    )

    if token_data.user_id is None:
        raise credentials_exception

    user = await session.get(User, token_data.user_id)
    if user is None:
        raise credentials_exception

    return user


def get_current_admin(
        current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user

