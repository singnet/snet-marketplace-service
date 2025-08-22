from deployer.application.schemas.daemon_schemas import DaemonRequest, UpdateConfigRequest, SearchDaemonRequest
from deployer.exceptions import DaemonNotFoundException
from deployer.infrastructure.clients.deployer_cleint import DeployerClient
from deployer.infrastructure.clients.haas_client import HaaSClient
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.models import DaemonStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.claiming_period_repository import ClaimingPeriodRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository


class DaemonService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self._deployer_client = DeployerClient()
        self._haas_client = HaaSClient()

    def get_user_daemons(self, account_id: str) -> list[dict]:
        with session_scope(self.session_factory) as session:
            user_daemons = DaemonRepository.get_user_daemons(session, account_id)
        # TODO: add other fields
        return [daemon.to_short_response() for daemon in user_daemons]

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
        with session_scope(self.session_factory) as session:
            # TODO: check status
            ClaimingPeriodRepository.create_claiming_period(session, request.daemon_id)
            self._deployer_client.start_daemon(request.daemon_id)
        return {}

    def start_daemon(self, request: DaemonRequest):
        daemon_id = request.daemon_id

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)

            if daemon is None:
                raise DaemonNotFoundException(daemon_id)

            org_id = daemon.org_id
            service_id = daemon.service_id
            daemon_config = daemon.daemon_config

            if daemon.status != DaemonStatus.READY_TO_START or not daemon.service_published:
                return {}

            self._haas_client.start_daemon(
                org_id = org_id,
                service_id = service_id,
                daemon_config = daemon_config
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

            self._haas_client.delete_daemon(org_id, service_id)
            DaemonRepository.update_daemon_status(session, daemon_id, DaemonStatus.DELETING)

        return {}

    def redeploy_daemon(self, request: DaemonRequest):
        daemon_id = request.daemon_id

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)

            if daemon is None:
                raise DaemonNotFoundException(daemon_id)

            org_id = daemon.org_id
            service_id = daemon.service_id
            daemon_config = daemon.daemon_config

            if daemon.status != DaemonStatus.UP:
                return {}

            self._haas_client.redeploy_daemon(
                org_id = org_id,
                service_id = service_id,
                daemon_config = daemon_config
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

            # TODO: check status

            daemon_config = daemon.daemon_config
            if service_endpoint:
                daemon_config["service_endpoint"] = service_endpoint
            if service_credentials:
                daemon_config["service_credentials"] = service_credentials

            DaemonRepository.update_daemon_config(session, request.daemon_id, daemon_config)

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
            return {"daemon": daemon.to_response(), "order": order.to_short_response()}

    def pause_daemon(self, request: DaemonRequest):
        pass

    def unpause_daemon(self, request: DaemonRequest):
        pass