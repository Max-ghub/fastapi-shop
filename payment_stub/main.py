from typing import Any

from fastapi import FastAPI
from schemas import CreatePaymentIn, CreatePaymentOut, PaymentStatusOut

app = FastAPI()
_PAYMENTS: dict[str, int] = {}


@app.post("/payments", response_model=CreatePaymentOut)
def create_payment(payload: CreatePaymentIn) -> dict[str, Any]:
    _PAYMENTS[payload.payment_id] = payload.order_id
    return {"payment_id": payload.payment_id, "status": "pending"}


@app.get("/payments/{payment_id}", response_model=PaymentStatusOut)
def get_payment_status(payment_id: str) -> dict[str, Any]:
    order_id = _PAYMENTS.get(payment_id, 0)
    status = "paid" if payment_id in _PAYMENTS else "failed"
    return {"payment_id": payment_id, "order_id": order_id, "status": status}
