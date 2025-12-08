from pydantic import BaseModel, ConfigDict


class CartItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cart_id: int | None
    product_id: int | None
    quantity: int


class CartRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    items: list[CartItemRead]
