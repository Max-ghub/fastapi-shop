from pydantic import BaseModel, ConfigDict


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    price_amount: int
    currency: str
    stock: int
    is_active: bool
    category_id: int | None


class ProductCreate(BaseModel):
    name: str
    slug: str
    description: str | None
    price_amount: int
    currency: str
    stock: int
    is_active: bool
    category_id: int | None


class ProductUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    price_amount: int | None = None
    currency: str | None = None
    stock: int | None = None
    is_active: bool | None = None
    category_id: int | None = None
