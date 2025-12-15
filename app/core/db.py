from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):  # type: ignore[misc]
    pass


_engine: AsyncEngine = create_async_engine(
    settings.database_dsn,
    echo=False,
)

SessionLocal = async_sessionmaker(
    bind=_engine,
    expire_on_commit=False,
)


def get_engine() -> AsyncEngine:
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
