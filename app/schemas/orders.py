from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import CurrencyEnum, OrderStatusEnum


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    price_minor: int = Field(ge=0)
    quantity: int = Field(ge=1)


class OrderSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    total_amount: int = Field(ge=0)
    currency: CurrencyEnum
    status: OrderStatusEnum
    created_at: datetime


class OrderRead(OrderSummary):
    items: list[OrderItemRead]


class OrderList(BaseModel):
    items: list[OrderSummary]


class OrderCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: OrderStatusEnum
