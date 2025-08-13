from common.utils import generate_uuid
from deployer.application.schemas.order_schemas import InitiateOrderRequest, GetOrderRequest
from deployer.domain.models.daemon import NewDaemonDomain
from deployer.domain.models.order import NewOrderDomain
from deployer.infrastructure.db import in_session
from deployer.infrastructure.models import DaemonStatus, OrderStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository


class OrderService:
    def __init__(self):
        self._order_repo = OrderRepository()
        self._daemon_repo = DaemonRepository()

    @in_session
    def initiate_order(self, request: InitiateOrderRequest):
        daemon_id = generate_uuid()
        self._daemon_repo.create_daemon(
            NewDaemonDomain(
                id=daemon_id,
                account_id=request.account_id,
                org_id=request.org_id,
                service_id=request.service_id,
                status=DaemonStatus.INIT,
                daemon_config={
                    "service_endpoint": request.service_endpoint,
                    "payment_channel_storage_type": request.storage_type,
                    "service_cred_key": request.parameters.get("key"),
                    "service_cred_value": request.parameters.get("value"),
                    "service_cred_location": request.parameters.get("location"),
                },
            )
        )

        order_uuid = generate_uuid()
        self._order_repo.create_order(
            NewOrderDomain(
                id=order_uuid,
                daemon_id=daemon_id,
                status=OrderStatus.PROCESSING
            )
        )

    @in_session
    def get_order(self, request: GetOrderRequest) -> dict:
        order = self._order_repo.get_order(request.order_id)
        return order.to_response()

