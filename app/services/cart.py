from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models.cart import CartItem
from app.models.user import User
from app.repositories.cart import CartRepository
from app.schemas.carts import CartItemRead, CartItemUpdate, CartRead


def _not_found(what: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"{what} not found"
    )


def _conflict(msg: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)


class CartService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repo = CartRepository(db_session)

    async def get_cart(self, user: User) -> CartRead:
        cart = await self.repo.get_cart(user.id)
        if cart is None:
            raise _not_found("Cart")
        return CartRead.model_validate(cart)

    async def update_cart_item(
        self, user: User, item_id: int, payload: CartItemUpdate
    ) -> CartItemRead:
        item = await self.repo.get_item_for_user(user.id, item_id, with_product=True)
        if item is None:
            raise _not_found("Item")

        if payload.quantity > item.product.stock:
            raise _conflict("Not enough stock")

        updated = await self.repo.set_item_quantity(item, payload.quantity)
        return CartItemRead.model_validate(updated)

    async def add_cart_item(
        self, user: User, product_id: int, quantity: int
    ) -> CartItemRead:
        cart = await self.repo.get_cart(user.id, with_products=False)
        if cart is None:
            raise _not_found("Cart")

        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
        )

        created = await self.repo.add_item(item)
        return CartItemRead.model_validate(created)

    async def delete_cart_item(self, user: User, item_id: int) -> None:
        item = await self.repo.get_item_for_user(user.id, item_id, with_product=False)
        if item is None:
            raise _not_found("Item")
        await self.repo.delete_item(item)
