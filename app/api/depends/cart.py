from typing import Annotated

from fastapi import Depends

from app.api.depends.db import SessionDep
from app.services.cart import CartService


def _get_cart_service(db_session: SessionDep) -> CartService:
    return CartService(db_session)


CartServiceDep = Annotated[CartService, Depends(_get_cart_service)]
