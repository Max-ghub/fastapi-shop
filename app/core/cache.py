import hashlib
from typing import cast

from fastapi import Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


def make_query_key_builder(prefix: str):
    """
    Key look like: "{prefix}:{md5(sorted_query_params)}"
    Example: "catalog:list:e132a29eac93af2d0c857343c91b8eec"
    """
    def key_builder(
        func,
        namespace: str,
        request: Request,
        response=None,
        *args,
        **kwargs,
    ) -> str:
        items = sorted(request.query_params.multi_items())
        raw = "&".join(f"{k}={v}" for k, v in items)
        digest = hashlib.md5(raw.encode("utf-8")).hexdigest()
        return f"{prefix}:{digest}"

    return key_builder


def make_path_key_builder(prefix: str, param_name: str):
    """
    Key look like: "{prefix}:{value}"
    Example: "catalog:product:42" or "catalog:product:iphone-15"
    """
    def key_builder(
        func,
        namespace: str,
        request: Request,
        response=None,
        *args,
        **kwargs,
    ) -> str:
        value = request.path_params.get(param_name)
        return f"{prefix}:{value}"

    return key_builder

async def invalidate_list(prefix: str) -> None:
    """
    Delete all keys look like: "{prefix}:list:*"
    """
    backend = FastAPICache.get_backend()
    redis_backend = cast(RedisBackend, backend)
    redis = redis_backend.redis

    pattern = f"{prefix}:list:*"
    async for key in redis.scan_iter(match=pattern):
        await redis.delete(key)

async def invalidate_item(prefix: str, *idents: str | int) -> None:
    """
    Delete keys like: "{prefix}:item:{ident}"
    Supports multiple identifiers (id, slug, etc).
    """
    backend = FastAPICache.get_backend()
    redis_backend = cast(RedisBackend, backend)
    redis = redis_backend.redis

    for ident in idents:
        await redis.delete(f"{prefix}:item:{ident}")