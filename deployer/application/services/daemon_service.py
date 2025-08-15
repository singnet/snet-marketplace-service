from deployer.application.schemas.daemon_schemas import DaemonRequest
from deployer.infrastructure.clients.deployer_cleint import DeployerClient
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.claiming_period_repository import ClaimingPeriodRepository


class DaemonService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self.deployer_client = DeployerClient()

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
        pass

    def stop_daemon(self, request: DaemonRequest):
        pass

    def pause_daemon(self, request: DaemonRequest):
        pass

    def unpause_daemon(self, request: DaemonRequest):
        pass
