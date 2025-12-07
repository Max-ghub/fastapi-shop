from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.depends import CurrentUserDep, UserServiceDep
from app.schemas.auth import Token
from app.schemas.users import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    path="/register", response_model=UserOut, status_code=status.HTTP_201_CREATED
)
async def register(user: UserCreate, service: UserServiceDep) -> UserOut:
    return await service.create_user(user)


@router.post(path="/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], service: UserServiceDep
) -> Token:
    return await service.authenticate_user(form_data.username, form_data.password)


@router.get(path="/me", response_model=UserOut)
async def me(current_user: CurrentUserDep) -> UserOut:
    return UserOut.model_validate(current_user)
