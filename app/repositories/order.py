from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem


class OrderRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_by_id(self, order_id: int) -> Order | None:
        stmt = select(Order).where(Order.id == order_id)
        return await self.db_session.scalar(stmt)

    async def get_with_items(self, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
        )
        return await self.db_session.scalar(stmt)

    async def get_item(self, user_id: int, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(
                Order.id == order_id,
                Order.user_id == user_id,
            )
            .options(selectinload(Order.items))
        )
        return await self.db_session.scalar(stmt)

    async def get_list(self, user_id: int) -> list[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        result = await self.db_session.scalars(stmt)
        return list(result.all())

    async def save(self, order: Order) -> Order:
        self.db_session.add(order)
        await self.db_session.flush()
        return order
