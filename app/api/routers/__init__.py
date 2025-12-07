from fastapi import APIRouter

from app.api.routers.auth import router as auth_router
from app.api.routers.category import router as categories_router
from app.api.routers.media import router as media_router
from app.api.routers.product import router as product_router
from app.api.routers.product_image import router as product_image_router

router = APIRouter(prefix="/api")
router.include_router(router=auth_router)
router.include_router(router=categories_router)
router.include_router(router=media_router)
router.include_router(router=product_router)
router.include_router(router=product_image_router)

__all__ = ["router"]
