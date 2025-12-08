from fastapi import APIRouter
from starlette import status

from app.api.depends import CartServiceDep, CurrentUserDep
from app.schemas.carts import CartRead

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get(path="/", response_model=CartRead, status_code=status.HTTP_200_OK)
async def get_cart(
    current_user: CurrentUserDep,
    service: CartServiceDep,
) -> CartRead:
    cart = await service.get_cart_by_user(current_user.id)
    return cart
