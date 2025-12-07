from fastapi import APIRouter
from starlette import status

from app.api.depends import AdminUserDep, CategoryServiceDep, CurrentUserDep
from app.schemas.categories import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "",
    response_model=list[CategoryRead],
    status_code=status.HTTP_200_OK,
)
async def read_categories(
    _current_user: CurrentUserDep, service: CategoryServiceDep
) -> list[CategoryRead]:
    categories = await service.get_categories()
    return categories


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    _admin_user: AdminUserDep,
    service: CategoryServiceDep,
    data: CategoryCreate,
) -> CategoryRead:
    new_category = await service.create_category(**data.model_dump())
    return new_category
