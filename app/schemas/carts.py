from pydantic import BaseModel, ConfigDict


class ProductInCart(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price: int
    stock: int
    is_active: bool
    quantity: int

class CartItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    quantity: int
    product: ProductInCart


class CartRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[CartItemRead]
