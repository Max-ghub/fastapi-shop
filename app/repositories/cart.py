from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Cart, CartItem


class CartRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_cart_with_items(self, user_id: int) -> Cart | None:
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items).selectinload(CartItem.product)
            )
        )
        cart = await self.db_session.scalar(stmt)
        return cart
