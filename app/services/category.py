from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions import conflict, not_found
from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.categories import CategoryList, CategoryRead


class CategoryService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repo = CategoryRepository(db_session)

    async def _get_category(self, category_id: int) -> Category:
        category = await self.repo.get_by_id(category_id)
        if category is None:
            raise not_found("Category")
        return category

    async def get_categories(self) -> CategoryList:
        items = await self.repo.get_list()
        return CategoryList.model_validate({"items": items})

    async def create_category(self, data: dict[str, Any]) -> CategoryRead:
        category = Category(**data)

        try:
            created = await self.repo.save(category)
        except IntegrityError:
            raise conflict("Category already exists") from None

        return CategoryRead.model_validate(created)

    async def update_category(
        self, category_id: int, data: dict[str, Any]
    ) -> CategoryRead:
        category = await self._get_category(category_id)

        try:
            updated = await self.repo.update(category, data)
        except IntegrityError:
            raise conflict("Category already exists") from None

        return CategoryRead.model_validate(updated)

    async def delete_category(self, category_id: int) -> None:
        category = await self._get_category(category_id)
        await self.repo.delete(category)
