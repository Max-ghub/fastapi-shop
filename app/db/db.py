from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.core.config import settings

_engine: AsyncEngine = create_async_engine(
    settings.database_dsn,
    echo=False,
)

SessionLocal = async_sessionmaker(
    bind=_engine,
    expire_on_commit=False,
)
