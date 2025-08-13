from deployer.application.schemas.daemon_schemas import DaemonRequest


class DaemonService:
    def __init__(self):
        pass

    def get_user_daemons(self, username: str):
        pass

    def get_service_daemon(self, request: DaemonRequest):
        pass

    def start_daemon_for_claiming(self, request: DaemonRequest):
        pass

    def start_daemon(self, request: DaemonRequest):
        pass

    def stop_daemon(self, request: DaemonRequest):
        pass

    def pause_daemon(self, request: DaemonRequest):
        pass

    def unpause_daemon(self, request: DaemonRequest):
        pass