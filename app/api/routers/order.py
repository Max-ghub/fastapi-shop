from fastapi import APIRouter
from starlette import status

from app.api.depends import CurrentUserDep, OrderServiceDep
from app.schemas.orders import OrderCreateResponse, OrderList, OrderRead
from app.tasks.orders import process_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get(
    path="/{order_id}",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
)
async def get_order(
    current_user: CurrentUserDep, service: OrderServiceDep, order_id: int
) -> OrderRead:
    return await service.get_order(current_user, order_id)


@router.get(path="", response_model=OrderList, status_code=status.HTTP_200_OK)
async def get_orders(
    current_user: CurrentUserDep,
    service: OrderServiceDep,
) -> OrderList:
    return await service.get_orders(current_user)


@router.post(
    path="",
    response_model=OrderCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    current_user: CurrentUserDep,
    service: OrderServiceDep,
) -> OrderCreateResponse:
    response = await service.create_order(current_user)

    order_id = response.id
    process_order.delay(order_id)

    return response
