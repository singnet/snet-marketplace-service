from datetime import datetime, UTC

from common.utils import generate_uuid
from deployer.application.schemas.order_schemas import InitiateOrderRequest, GetOrderRequest
from deployer.config import DEFAULT_DAEMON_STORAGE_TYPE
from deployer.domain.models.daemon import NewDaemonDomain
from deployer.domain.models.order import NewOrderDomain
from deployer.exceptions import MissingServiceEndpointException
from deployer.infrastructure.db import session_scope, DefaultSessionFactory
from deployer.infrastructure.models import DaemonStatus, OrderStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.utils import get_daemon_endpoint


class OrderService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory

    def initiate_order(self, request: InitiateOrderRequest):
        daemon_id = generate_uuid()
        order_uuid = generate_uuid()

        current_time = datetime.now(UTC)

        daemon_config = {
            "payment_channel_storage_type": DEFAULT_DAEMON_STORAGE_TYPE.value
        }
        if request.service_endpoint is not None:
            daemon_config["service_endpoint"] = request.service_endpoint
        if request.service_credentials is not None:
            daemon_config["service_credentials"] = request.service_credentials

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.search_daemon(session, request.org_id, request.service_id)
            if daemon is None:
                if request.service_endpoint is None:
                    raise MissingServiceEndpointException()
                DaemonRepository.create_daemon(
                    session,
                    NewDaemonDomain(
                        id=daemon_id,
                        account_id=request.account_id,
                        org_id=request.org_id,
                        service_id=request.service_id,
                        status=DaemonStatus.INIT,
                        daemon_config=daemon_config,
                        service_published=False,
                        daemon_endpoint = get_daemon_endpoint(request.org_id, request.service_id),
                        start_on = current_time,
                        end_on = current_time
                    )
                )
            else:
                daemon_id = daemon.id
                if len(daemon_config.keys()) != 1:
                    new_daemon_config = daemon_config
                    daemon_config = daemon.daemon_config
                    daemon_config.update(new_daemon_config)
                    DaemonRepository.update_daemon_config(session, daemon_id, daemon_config)

            OrderRepository.create_order(
                session,
                NewOrderDomain(
                    id=order_uuid,
                    daemon_id=daemon_id,
                    status=OrderStatus.PROCESSING
                )
            )

        return {"order_id": order_uuid}

    def get_order(self, request: GetOrderRequest) -> dict:
        with session_scope(self.session_factory) as session:
            order = OrderRepository.get_order(session, request.order_id)
        return order.to_short_response()

