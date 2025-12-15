from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart, CartItem


def _cart_stmt(*, with_items: bool, with_products: bool) -> Select[tuple[Any]]:
    stmt = select(Cart)
    if with_items:
        items_opt = selectinload(Cart.items)
        if with_products:
            items_opt = items_opt.selectinload(CartItem.product)
        stmt = stmt.options(items_opt)
    return stmt


def _item_stmt(*, with_product: bool) -> Select[tuple[Any]]:
    stmt = select(CartItem)
    if with_product:
        stmt = stmt.options(selectinload(CartItem.product))
    return stmt


class CartRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_cart(
        self, user_id: int, *, with_products: bool = True
    ) -> Cart | None:
        stmt = _cart_stmt(with_items=True, with_products=with_products).where(
            Cart.user_id == user_id
        )
        return await self.db_session.scalar(stmt)

    async def get_item_for_user(
        self,
        user_id: int,
        item_id: int,
        *,
        with_product: bool = True,
    ) -> CartItem | None:
        stmt = (
            _item_stmt(with_product=with_product)
            .join(CartItem.cart)
            .where(Cart.user_id == user_id, CartItem.id == item_id)
        )
        return await self.db_session.scalar(stmt)

    async def get_item_by_id(
        self,
        item_id: int,
        *,
        with_product: bool = True,
    ) -> CartItem | None:
        stmt = _item_stmt(with_product=with_product).where(CartItem.id == item_id)
        return await self.db_session.scalar(stmt)

    async def add_item(self, item: CartItem) -> CartItem:
        self.db_session.add(item)
        await self.db_session.flush()

        stmt = (
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(CartItem.id == item.id)
        )
        created = await self.db_session.scalar(stmt)
        return created

    async def set_item_quantity(self, item: CartItem, quantity: int) -> CartItem:
        item.quantity = quantity
        await self.db_session.flush()
        return item

    async def delete_item(self, item: CartItem) -> None:
        await self.db_session.delete(item)
        await self.db_session.flush()
