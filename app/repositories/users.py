from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_user_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return await self.db_session.scalar(stmt)

    async def get_user_by_email(self, user_email: str) -> User | None:
        stmt = select(User).where(User.email == user_email)
        return await self.db_session.scalar(stmt)

    async def save(self, user: User) -> User:
        self.db_session.add(user)
        await self.db_session.flush()
        return user
