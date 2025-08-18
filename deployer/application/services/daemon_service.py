from deployer.application.schemas.daemon_schemas import DaemonRequest
from deployer.infrastructure.clients.deployer_cleint import DeployerClient
from deployer.infrastructure.clients.haas_client import HaaSClient
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.models import DaemonStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.claiming_period_repository import ClaimingPeriodRepository


class DaemonService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self.deployer_client = DeployerClient()
        self.haas_client = HaaSClient()

    def get_user_daemons(self, username: str) -> list[dict]:
        with session_scope(self.session_factory) as session:
            user_daemons = DaemonRepository.get_user_daemons(session, username)
        return [daemon.to_short_response() for daemon in user_daemons]

    def get_service_daemon(self, request: DaemonRequest) -> dict:
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, request.daemon_id)
        return daemon.to_response()

    def start_daemon_for_claiming(self, request: DaemonRequest):
        with session_scope(self.session_factory) as session:
            ClaimingPeriodRepository.create_claiming_period(session, request.daemon_id)

            self.deployer_client.start_daemon(request.daemon_id)

    def start_daemon(self, request: DaemonRequest):
        daemon_id = request.daemon_id

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)
            org_id = daemon.org_id
            service_id = daemon.service_id
            daemon_config = daemon.daemon_config

            if daemon.status != DaemonStatus.READY_TO_START or not daemon.service_published:
                return

            self.haas_client.start_daemon(
                org_id = org_id,
                service_id = service_id,
                daemon_config = daemon_config
            )

            DaemonRepository.update_daemon_status(session, daemon_id, DaemonStatus.STARTING)

    def stop_daemon(self, request: DaemonRequest):
        daemon_id = request.daemon_id

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)
            org_id = daemon.org_id
            service_id = daemon.service_id

            if daemon.status != DaemonStatus.UP:
                return

            self.haas_client.delete_daemon(org_id, service_id)
            DaemonRepository.update_daemon_status(session, daemon_id, DaemonStatus.DELETING)

    def pause_daemon(self, request: DaemonRequest):
        pass

    def unpause_daemon(self, request: DaemonRequest):
        pass

    def get_public_key(self) -> dict:
        public_key = self.haas_client.get_public_key()
        return {"publicKey": public_key}
