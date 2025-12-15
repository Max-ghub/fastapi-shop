from fastapi import APIRouter
from starlette import status

from app.api.depends import CartServiceDep, CurrentUserDep
from app.schemas.carts import CartItemRead, CartItemUpdate, CartRead

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get(path="/", response_model=CartRead, status_code=status.HTTP_200_OK)
async def get_cart(
    current_user: CurrentUserDep,
    service: CartServiceDep,
) -> CartRead:
    return await service.get_cart(user=current_user)


@router.patch(
    path="/items/{item_id}", response_model=CartItemRead, status_code=status.HTTP_200_OK
)
async def update_cart_item(
    current_user: CurrentUserDep,
    service: CartServiceDep,
    item_id: int,
    payload: CartItemUpdate,
) -> CartItemRead:
    return await service.update_cart_item(current_user, item_id, payload)


@router.post(
    path="/items/{product_id}/{quantity}",
    response_model=CartItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_cart_item(
    current_user: CurrentUserDep,
    service: CartServiceDep,
    product_id: int,
    quantity: int,
) -> CartItemRead:
    return await service.add_cart_item(current_user, product_id, quantity)


@router.delete(path="/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(
    current_user: CurrentUserDep,
    service: CartServiceDep,
    item_id: int,
) -> None:
    await service.delete_cart_item(current_user, item_id)
