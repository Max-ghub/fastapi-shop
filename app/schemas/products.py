from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Currency(StrEnum):
    RUB = "RUB"


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    slug: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    price_minor: int = Field(ge=0)
    currency: Currency = Currency.RUB
    stock: int = Field(ge=0)
    is_active: bool = False
    category_id: int | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    slug: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    price_minor: int | None = Field(default=None, ge=0)
    currency: Currency | None = None
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    category_id: int | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    description: str | None
    price_minor: int
    currency: Currency
    stock: int
    is_active: bool
    category_id: int | None


class ProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price_minor: int
    stock: int
    is_active: bool


class ProductList(BaseModel):
    items: list[ProductSummary]
