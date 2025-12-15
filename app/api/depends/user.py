from typing import Annotated, Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from starlette import status

from app.api.depends.db import SessionDep
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.auth import TokenData
from app.services import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def _get_user_service(db_session: SessionDep) -> UserService:
    return UserService(db_session)


UserServiceDep = Annotated[UserService, Depends(_get_user_service)]


async def get_current_user(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload: dict[str, Any] = decode_access_token(token=token)
    except JWTError as error:
        raise credentials_exception from error

    token_data = TokenData(
        user_id=payload.get("user_id"),
        role=payload.get("role"),
    )

    if token_data.user_id is None:
        raise credentials_exception

    user: User | None = await session.get(User, token_data.user_id)
    if user is None:
        raise credentials_exception

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def get_current_admin(current_user: CurrentUserDep) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


AdminUserDep = Annotated[User, Depends(get_current_admin)]

__all__ = ["UserServiceDep", "CurrentUserDep", "AdminUserDep"]
