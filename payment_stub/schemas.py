from enum import Enum

from pydantic import BaseModel


class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"


class PaymentStatusOut(BaseModel):
    payment_id: str
    order_id: int
    status: PaymentStatus


class CreatePaymentIn(BaseModel):
    order_id: int
    amount: int
    payment_id: str


class CreatePaymentOut(BaseModel):
    payment_id: str
    status: PaymentStatus
