from pydantic import BaseModel, ConfigDict, Field

from app.schemas.products import ProductSummary


class ItemInCart(ProductSummary):
    pass


class CartItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    quantity: int
    item: ItemInCart = Field(validation_alias="product")


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    items: list[CartItemRead]
