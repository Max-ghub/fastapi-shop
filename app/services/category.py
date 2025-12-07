from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from app.repositories.category import CategoryRepository
from app.schemas.categories import CategoryRead


class CategoryService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repo = CategoryRepository(db_session)

    async def get_categories(self) -> list[CategoryRead]:
        categories = await self.repo.list_categories()
        return [CategoryRead.model_validate(category) for category in categories]

    async def create_category(self, **data: Any) -> CategoryRead:
        category_db = Category(**data)
        created_category = await self.repo.save(category_db)
        return CategoryRead.model_validate(created_category)
