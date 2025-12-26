from enum import StrEnum
from typing import Any


def enum_values(enum_cls: Any) -> list[str]:
    return [e.value for e in enum_cls]


class CurrencyEnum(StrEnum):
    RUB = "RUB"


class OrderStatusEnum(StrEnum):
    CREATED = "created"
    PROCESSING = "processing"
    PAID = "paid"
    CANCELLED = "cancelled"


class PaymentStatusEnum(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    DONE = "done"
