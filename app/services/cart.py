from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions import conflict, not_found
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.repositories.cart import CartRepository
from app.schemas.carts import CartItemRead, CartItemUpdate, CartRead


class CartService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repo = CartRepository(db_session)

    async def get_cart(self, user: User) -> CartRead:
        cart = await self.repo.get_cart(user.id)
        if cart is None:
            raise not_found("Cart")
        return CartRead.model_validate(cart)

    async def update_cart_item(
        self, user: User, item_id: int, payload: CartItemUpdate
    ) -> CartItemRead:
        item = await self.repo.get_item_for_user(user.id, item_id, with_product=True)
        if item is None:
            raise not_found("Item")

        if payload.quantity > item.product.stock:
            raise conflict("Not enough stock")

        updated = await self.repo.set_item_quantity(item, payload.quantity)
        return CartItemRead.model_validate(updated)

    async def add_cart_item(
        self, user: User, product_id: int, quantity: int
    ) -> CartItemRead:
        if quantity <= 0:
            raise conflict("Quantity must be positive")

        product = await self.db_session.get(Product, product_id)
        if product is None:
            raise not_found("Product")
        if quantity > product.stock:
            raise conflict("Not enough stock")

        cart = await self.repo.get_cart(user.id, with_products=False)
        if cart is None:
            raise not_found("Cart")

        existing = await self.repo.get_item_by_cart_product(
            cart.id, product_id, with_product=True
        )
        if existing is not None:
            updated = await self.repo.set_item_quantity(existing, quantity)
            return CartItemRead.model_validate(updated)

        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        created = await self.repo.add_item(item)
        return CartItemRead.model_validate(created)

    async def delete_cart_item(self, user: User, item_id: int) -> None:
        item = await self.repo.get_item_for_user(user.id, item_id, with_product=False)
        if item is None:
            raise not_found("Item")
        await self.repo.delete_item(item)
