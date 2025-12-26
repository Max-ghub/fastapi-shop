import asyncio
import uuid
from typing import Any

import httpx
from celery import Task

from app.core.celery_app import celery_app
from app.core.db import transaction_scope
from app.domain.enums import OrderStatusEnum, PaymentStatusEnum
from app.models import Order
from app.repositories.order import OrderRepository

PAYMENT_URL = "http://payment_stub:8001/payments"
HTTP_TIMEOUT = 3.0
# Reuse one loop per worker process so asyncpg stays bound to a single loop.
_EVENT_LOOP: asyncio.AbstractEventLoop | None = None


def _run_async(coro: Any) -> Any:
    global _EVENT_LOOP
    if _EVENT_LOOP is None or _EVENT_LOOP.is_closed():
        _EVENT_LOOP = asyncio.new_event_loop()
        asyncio.set_event_loop(_EVENT_LOOP)
    return _EVENT_LOOP.run_until_complete(coro)


@celery_app.task(bind=True, name="order.process", max_retries=10)
def process_order(self: Task, order_id: int) -> None:
    try:
        result = _run_async(_process_order(order_id))
    except httpx.HTTPError as exc:
        raise self.retry(exc=exc, countdown=5) from exc

    if result == PaymentStatusEnum.PENDING:
        raise self.retry(countdown=10)


async def _process_order(order_id: int) -> PaymentStatusEnum:
    status, payment_id, amount, should_create = await _init_payment(order_id)
    if status is not None:
        return status
    if payment_id is None:
        return PaymentStatusEnum.DONE

    created = False
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            if should_create:
                response = await client.post(
                    url=PAYMENT_URL,
                    json={
                        "order_id": order_id,
                        "amount": amount,
                        "payment_id": str(payment_id),
                    },
                )
                response.raise_for_status()
                created = True

            response = await client.get(f"{PAYMENT_URL}/{payment_id}")
            response.raise_for_status()
            payment_status = response.json().get("status", PaymentStatusEnum.FAILED)
    except httpx.HTTPError:
        if should_create and not created:
            await _rollback_processing(order_id)
        raise

    return await _finalize_payment(order_id, payment_status)


async def _init_payment(
    order_id: int,
) -> tuple[PaymentStatusEnum | None, uuid.UUID | None, int, bool]:
    should_create = False
    payment_id = None
    amount = 0

    async with transaction_scope() as session:
        repo = OrderRepository(session)
        order = await repo.get_with_items(order_id)
        if order is None:
            return PaymentStatusEnum.DONE, None, 0, False

        if order.status == OrderStatusEnum.CREATED:
            if not _reserve_stock(order):
                order.status = OrderStatusEnum.CANCELLED
                return PaymentStatusEnum.FAILED, None, 0, False
            payment_id = uuid.uuid4()
            order.payment_id = payment_id
            order.status = OrderStatusEnum.PROCESSING
            should_create = True
        elif (
            order.status == OrderStatusEnum.PROCESSING and order.payment_id is not None
        ):
            payment_id = order.payment_id
        else:
            return PaymentStatusEnum.DONE, None, 0, False

        amount = order.total_amount

    return None, payment_id, amount, should_create


async def _finalize_payment(
    order_id: int,
    payment_status: PaymentStatusEnum,
) -> PaymentStatusEnum:
    async with transaction_scope() as session:
        repo = OrderRepository(session)
        order = await repo.get_with_items(order_id)

        if order is None or order.status != OrderStatusEnum.PROCESSING:
            return PaymentStatusEnum.DONE

        if payment_status == PaymentStatusEnum.PENDING:
            return PaymentStatusEnum.PENDING

        if payment_status == PaymentStatusEnum.PAID:
            order.status = OrderStatusEnum.PAID
            return PaymentStatusEnum.PAID

        _restore_stock(order)
        order.status = OrderStatusEnum.CANCELLED
        return PaymentStatusEnum.FAILED


def _reserve_stock(order: Order) -> bool:
    for item in order.items:
        if item.product.stock < item.quantity:
            return False
    for item in order.items:
        item.product.stock -= item.quantity
    return True


def _restore_stock(order: Order) -> None:
    for item in order.items:
        item.product.stock += item.quantity


async def _rollback_processing(order_id: int) -> None:
    async with transaction_scope() as session:
        repo = OrderRepository(session)
        order = await repo.get_with_items(order_id)
        if order is None or order.status != OrderStatusEnum.PROCESSING:
            return
        _restore_stock(order)
        order.status = OrderStatusEnum.CREATED
        order.payment_id = None
