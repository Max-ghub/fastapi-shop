from typing import Annotated

from fastapi import Depends

from app.api.depends.db import SessionDep
from app.services import OrderService


def _get_order_service(db_session: SessionDep) -> OrderService:
    return OrderService(db_session)


OrderServiceDep = Annotated[OrderService, Depends(_get_order_service)]

__all__ = ["OrderServiceDep"]
