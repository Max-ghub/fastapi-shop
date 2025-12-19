# noqa: F401
from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context  # type: ignore
from app.core.db import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.models.cart import Cart, CartItem
from app.models.category import Category
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.user import User

target_metadata = Base.metadata


def _alembic_url() -> str:
    url = os.getenv("DATABASE_DSN")
    if not url:
        raise RuntimeError("DATABASE_DSN is not set")
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=_alembic_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_async_engine(_alembic_url(), pool_pre_ping=True)

    def do_run_migrations(connection: Connection) -> None:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    async def run() -> None:
        async with connectable.connect() as conn:
            await conn.run_sync(do_run_migrations)
        await connectable.dispose()

    asyncio.run(run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
