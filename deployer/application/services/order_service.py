from deployer.application.schemas.order_schemas import InitiateOrderRequest, GetOrderRequest
from deployer.infrastructure.db import in_session
from deployer.infrastructure.repositories.order_repository import OrderRepository


class OrderService:
    def __init__(self):
        self._order_repo = OrderRepository()

    def initiate_order(self, request: InitiateOrderRequest):
        pass

    @in_session
    def get_order(self, request: GetOrderRequest) -> dict:
        order = self._order_repo.get_order(request.order_id)
        return order.to_response()