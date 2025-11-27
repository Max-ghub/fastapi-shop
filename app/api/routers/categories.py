from fastapi import APIRouter
from sqlalchemy import select
from starlette import status

from app.api.depends import AdminUserDep, CurrentUserDep, SessionDep
from app.models import Category
from app.schemas.categories import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "",
    response_model=list[CategoryRead],
    status_code=status.HTTP_200_OK,
)
async def read_categories(
    current_user: CurrentUserDep,
    session: SessionDep,
) -> list[Category]:
    stmt = select(Category)
    result = await session.scalars(stmt)
    categories = list(result.all())
    return categories


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    admin_user: AdminUserDep,
    session: SessionDep,
    category: CategoryCreate,
) -> Category:
    db_category = Category(**category.model_dump())
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    return db_category
