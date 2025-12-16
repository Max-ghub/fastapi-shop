from fastapi import APIRouter
from starlette import status

from app.api.depends import AdminUserDep, CategoryServiceDep, CurrentUserDep
from app.schemas.categories import (
    CategoryCreate,
    CategoryList,
    CategoryRead,
    CategoryUpdate,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "",
    response_model=CategoryList,
    status_code=status.HTTP_200_OK,
)
async def read_categories(
    _current_user: CurrentUserDep, service: CategoryServiceDep
) -> CategoryList:
    categories = await service.get_categories()
    return categories


@router.post(
    path="",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    _admin_user: AdminUserDep,
    service: CategoryServiceDep,
    payload: CategoryCreate,
) -> CategoryRead:
    return await service.create_category(payload.model_dump())


@router.patch(
    path="/{category_id}",
    response_model=CategoryRead,
    status_code=status.HTTP_200_OK,
)
async def update_category(
    category_id: int,
    _admin_user: AdminUserDep,
    service: CategoryServiceDep,
    payload: CategoryUpdate,
) -> CategoryRead:
    data = payload.model_dump(exclude_unset=True)
    return await service.update_category(category_id, data)


@router.delete(
    path="/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    _admin_user: AdminUserDep,
    service: CategoryServiceDep,
    category_id: int,
) -> None:
    await service.delete_category(category_id)
