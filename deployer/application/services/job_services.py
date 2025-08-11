from deployer.application.schemas.job_schemas import RegistryEventConsumerRequest


class ServiceEventConsumer:
    def __init__(self):
        pass

    def on_event(self, request: RegistryEventConsumerRequest):
        event_name = request.event_name
        if event_name == "ServiceDeleted":
            self._delete_daemon(request)
        else:
            self._deploy_or_redeploy_daemon(request)

    def _deploy_or_redeploy_daemon(self, event):
        pass

    def _delete_daemon(self, event):
        pass


class JobService:
    def __init__(self):
        pass

    def update_transaction_status(self):
        pass