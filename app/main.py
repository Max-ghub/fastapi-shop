from contextlib import asynccontextmanager
from typing import AsyncIterator

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.api.routers.auth import router as auth_router
from app.api.routers.categories import router as categories_router
from app.api.routers.media import router as media_router
from app.api.routers.products import router as product_router
from app.core.config import settings
from app.core.metrics import setup_metrics


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis_client = redis.from_url(
        settings.redis_dsn,
        encoding="utf-8",
        decode_responses=True,
    )

    FastAPICache.init(
        RedisBackend(redis_client),
        prefix="cache",
    )

    yield


app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
app.include_router(router=auth_router)
app.include_router(router=product_router)
app.include_router(router=categories_router)
app.include_router(router=media_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


setup_metrics(app)
