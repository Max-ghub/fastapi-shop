from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_by_id(self, category_id: int) -> Category | None:
        stmt = select(Category).where(Category.id == category_id)
        return await self.db_session.scalar(stmt)

    async def get_list(self) -> list[Category]:
        stmt = select(Category)
        result = await self.db_session.scalars(stmt)
        categories = list(result.all())
        return categories

    async def update(self, category: Category, data: dict[str, Any]) -> Category:
        for key, value in data.items():
            setattr(category, key, value)
        await self.db_session.flush()
        return category

    async def save(self, category: Category) -> Category:
        self.db_session.add(category)
        await self.db_session.flush()
        return category

    async def delete(self, category: Category) -> None:
        await self.db_session.delete(category)
        await self.db_session.flush()
