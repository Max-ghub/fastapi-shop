from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.repositories.cart import CartRepository
from app.schemas.carts import CartRead


class CartService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repo = CartRepository(db_session)

    async def get_cart_by_user(self, user_id: int) -> CartRead:
        cart = await self.repo.get_cart_with_items(user_id)
        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
            )
        return CartRead.model_validate(cart)
