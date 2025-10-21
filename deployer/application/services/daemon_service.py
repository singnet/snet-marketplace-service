from datetime import UTC, datetime, timedelta
from typing import List

from common.logger import get_logger
from deployer.application.schemas.daemon_schemas import (
    DaemonRequest,
    UpdateConfigRequest,
    SearchDaemonRequest,
)
from deployer.config import BREAK_PERIOD_IN_HOURS
from deployer.exceptions import (
    DaemonNotFoundException,
    ClaimingNotAvailableException,
    UpdateConfigNotAvailableException,
)
from deployer.infrastructure.clients.deployer_client import DeployerClient
from deployer.infrastructure.clients.haas_client import HaaSClient
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.models import DaemonStatus, ClaimingPeriodStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.claiming_period_repository import ClaimingPeriodRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository


logger = get_logger(__name__)


class DaemonService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self._deployer_client = DeployerClient()
        self._haas_client = HaaSClient()

    def get_user_daemons(self, account_id: str) -> List[dict]:
        result = []

        with session_scope(self.session_factory) as session:
            user_daemons = DaemonRepository.get_user_daemons(session, account_id)
            daemon_ids = [daemon.id for daemon in user_daemons]

            claiming_periods = ClaimingPeriodRepository.get_last_claiming_periods_batch(
                session, daemon_ids
            )
            orders = OrderRepository.get_last_successful_orders_batch(session, daemon_ids)

        for daemon in user_daemons:
            daemon_response = daemon.to_short_response()

            last_claiming_period = claiming_periods.get(daemon.id, None)
            if last_claiming_period is not None:
                daemon_response.update(last_claiming_period.to_daemon_response())
            else:
                daemon_response["lastClaimedAt"] = ""

            order = orders.get(daemon.id, None)
            daemon_response["lastPayment"] = (
                order.updated_at.isoformat() if order is not None else ""
            )

            result.append(daemon_response)

        return result

    def get_service_daemon(self, request: DaemonRequest) -> dict:
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, request.daemon_id)
            if daemon is None:
                raise DaemonNotFoundException(request.daemon_id)
            orders = OrderRepository.get_daemon_orders(session, request.daemon_id)

        result = daemon.to_response()
        result["orders"] = [order.to_response() for order in orders]

        return result

    def start_daemon_for_claiming(self, request: DaemonRequest):
        current_time = datetime.now(UTC)
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, request.daemon_id)
            if daemon is None:
                raise DaemonNotFoundException(request.daemon_id)
            if daemon.status != DaemonStatus.DOWN:
                raise ClaimingNotAvailableException(reason="status")
            last_claiming_period = ClaimingPeriodRepository.get_last_claiming_period(
                session, request.daemon_id
            )
            if (
                last_claiming_period is not None
                and last_claiming_period.status != ClaimingPeriodStatus.FAILED
                and last_claiming_period.end_at + timedelta(hours=BREAK_PERIOD_IN_HOURS)
                > current_time
            ):
                raise ClaimingNotAvailableException(
                    reason="time", last_claimed_at=last_claiming_period.end_at.isoformat()
                )
            ClaimingPeriodRepository.create_claiming_period(session, request.daemon_id)
            self._deployer_client.start_daemon(request.daemon_id)
        return {}

    def start_daemon(self, request: DaemonRequest):
        daemon_id = request.daemon_id

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)

            if daemon is None:
                raise DaemonNotFoundException(daemon_id)

            if daemon.status != DaemonStatus.READY_TO_START or not daemon.service_published:
                return {}

            logger.info(f"Starting daemon: {daemon.to_response()}")
            self._haas_client.start_daemon(
                org_id=daemon.org_id,
                service_id=daemon.service_id,
                daemon_config=daemon.daemon_config,
            )

            DaemonRepository.update_daemon_status(session, daemon_id, DaemonStatus.STARTING)

        return {}

    def stop_daemon(self, request: DaemonRequest):
        daemon_id = request.daemon_id

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)

            if daemon is None:
                raise DaemonNotFoundException(daemon_id)

            org_id = daemon.org_id
            service_id = daemon.service_id

            if daemon.status != DaemonStatus.UP:
                return {}

            logger.info(f"Stopping daemon: {daemon.to_response()}")
            self._haas_client.delete_daemon(org_id, service_id)
            DaemonRepository.update_daemon_status(session, daemon_id, DaemonStatus.DELETING)

        return {}

    def redeploy_daemon(self, request: DaemonRequest):
        daemon_id = request.daemon_id

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)

            if daemon is None:
                raise DaemonNotFoundException(daemon_id)

            if daemon.status != DaemonStatus.UP:
                return {}

            logger.info(f"Redeploying daemon: {daemon.to_response()}")
            self._haas_client.redeploy_daemon(
                org_id=daemon.org_id,
                service_id=daemon.service_id,
                daemon_config=daemon.daemon_config,
            )

            DaemonRepository.update_daemon_status(session, daemon_id, DaemonStatus.RESTARTING)

        return {}

    def get_public_key(self) -> dict:
        public_key = self._haas_client.get_public_key()
        return {"publicKey": public_key}

    def update_config(self, request: UpdateConfigRequest) -> dict:
        service_endpoint = request.service_endpoint
        service_credentials = request.service_credentials
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, request.daemon_id)
            if daemon is None:
                raise DaemonNotFoundException(request.daemon_id)

            if daemon.status in [DaemonStatus.STARTING, DaemonStatus.RESTARTING]:
                raise UpdateConfigNotAvailableException()

            daemon_config = daemon.daemon_config
            if service_endpoint:
                daemon_config["service_endpoint"] = service_endpoint
            if service_credentials:
                daemon_config["service_credentials"] = service_credentials

            DaemonRepository.update_daemon_config(session, request.daemon_id, daemon_config)

            if daemon.status == DaemonStatus.UP:
                self._deployer_client.redeploy_daemon(request.daemon_id)

        return {}

    def search_daemon(self, request: SearchDaemonRequest) -> dict:
        org_id = request.org_id
        service_id = request.service_id
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.search_daemon(session, org_id, service_id)
            if daemon is None:
                return {}
            order = OrderRepository.get_last_order(session, daemon.id)
        daemon_response = daemon.to_response()
        del daemon_response["daemonConfig"]
        return {"daemon": daemon_response, "order": order.to_short_response()}

    def pause_daemon(self, request: DaemonRequest):
        pass

    def unpause_daemon(self, request: DaemonRequest):
        pass
