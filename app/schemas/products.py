from pydantic import BaseModel, ConfigDict


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    description: str | None
    price: int
    currency: str
    stock: int
    is_active: bool
    category_id: int | None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price: int
    stock: int
    is_active: bool


class ProductCreate(BaseModel):
    name: str
    slug: str
    description: str | None
    price: int
    currency: str
    stock: int
    is_active: bool
    category_id: int | None


class ProductUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    price: int | None = None
    currency: str | None = None
    stock: int | None = None
    is_active: bool | None = None
    category_id: int | None = None
