from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select, select

from app.db.db import SessionLocal


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def add(model: Any, session: AsyncSession) -> None:
    session.add(model)
    await session.commit()
    await session.refresh(model)


async def exists(stmt: Select, session: AsyncSession) -> bool:
    return await session.scalar(select(stmt.exists()))
