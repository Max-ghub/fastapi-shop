from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.exceptions import not_found
from app.domain.enums import CurrencyEnum, OrderStatusEnum
from app.models.cart import Cart
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.repositories.cart import CartRepository
from app.repositories.order import OrderRepository
from app.schemas.orders import OrderCreateResponse, OrderList, OrderRead


class OrderService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.order_repo = OrderRepository(db_session)
        self.cart_repo = CartRepository(db_session)

    async def get_order(self, user: User, order_id: int) -> OrderRead:
        order = await self.order_repo.get_item(user.id, order_id)
        if order is None:
            raise not_found("Order")
        return OrderRead.model_validate(order)

    async def get_orders(self, user: User) -> OrderList:
        items = await self.order_repo.get_list(user.id)
        return OrderList.model_validate({"items": items})

    async def create_order(self, user: User) -> OrderCreateResponse:
        cart: Cart | None = await self.cart_repo.get_cart(user.id, with_products=True)

        if cart is None:
            raise not_found("Cart")
        if not cart.items:
            raise HTTPException(
                detail="Cart is empty",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        items: list[OrderItem] = []
        total_amount = 0

        for item in cart.items:
            product: Product = item.product
            price_minor = product.price_minor
            quantity = item.quantity

            items.append(
                OrderItem(
                    product_id=product.id, price_minor=price_minor, quantity=quantity
                )
            )
            total_amount += price_minor * quantity

        order = Order(
            user_id=user.id,
            total_amount=total_amount,
            currency=CurrencyEnum.RUB,
            status=OrderStatusEnum.CREATED,
            items=items,
        )

        await self.order_repo.save(order)
        # await self.cart_repo.delete_all(cart)
        return OrderCreateResponse.model_validate(order)
