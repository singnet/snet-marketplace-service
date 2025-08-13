from deployer.application.schemas.daemon_schemas import DaemonRequest
from deployer.infrastructure.db import in_session
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository


class DaemonService:
    def __init__(self):
        self._daemon_repo = DaemonRepository()

    @in_session
    def get_user_daemons(self, username: str) -> list[dict]:
        user_daemons = self._daemon_repo.get_user_daemons(username)
        return [daemon.to_short_response() for daemon in user_daemons]

    @in_session
    def get_service_daemon(self, request: DaemonRequest):
        daemon = self._daemon_repo.get_daemon(request.daemon_id)
        return daemon.to_response()

    @in_session
    def start_daemon_for_claiming(self, request: DaemonRequest):
        pass

    @in_session
    def start_daemon(self, request: DaemonRequest):
        pass

    @in_session
    def stop_daemon(self, request: DaemonRequest):
        pass

    @in_session
    def pause_daemon(self, request: DaemonRequest):
        pass

    @in_session
    def unpause_daemon(self, request: DaemonRequest):
        pass

    @in_session
    def delete_daemon(self, request: DaemonRequest):
        pass