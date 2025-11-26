from contextlib import asynccontextmanager
import redis.asyncio as redis

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.api.routers.auth import router as auth_router
from app.api.routers.products import router as product_router
from app.api.routers.categories import router as categories_router
from app.core.config import settings
from app.core.metrics import setup_metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
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

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}

@app.get("/")
async def root():
    return {"message": "Hello World"}

setup_metrics(app)
