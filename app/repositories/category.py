from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def list_categories(self) -> list[Category]:
        stmt = select(Category)
        result = await self.db_session.scalars(stmt)
        categories = list(result.all())
        return categories

    async def save(self, category: Category) -> Category:
        self.db_session.add(category)
        await self.db_session.flush()
        return category
