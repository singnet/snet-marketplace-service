from deployer.tests.functional.utils import generate_request_event


class TestDeploymentsEndpoints:
    def test_initiate_deployment_only_daemon_ok(self, test_deployments_service, test_session_factory, test_org_id, test_service_id):
        test_endpoint = "http://localhost:8080"
        test_credentials = [
            {"key": "Authorization", "value": "Bearer 1234567890", "location": "headers"}
        ]

        event = generate_request_event(
            body={
                "orgId": test_org_id,
                "serviceId": test_service_id,
                "onlyDaemon": True,
                "serviceEndpoint": test_endpoint,
                "serviceCredentials": test_credentials
            }
        )

    def test_initiate_deployment_ok(self, test_deployments_service, test_session_factory, test_org_id, test_service_id):
        test_account = "qwe"
        test_repo = "rty"

        event = generate_request_event(
            body = {
                "orgId": test_org_id,
                "serviceId": test_service_id,
                "onlyDaemon": False,
                "githubAccountName": test_account,
                "githubRepositoryName": test_repo
            }
        )

    def test_get_user_deployments(self, test_deployments_service):
        pass

    def test_search_deployments(self, test_deployments_service):
        pass

    def test_get_public_key(self, test_deployments_service):
        pass

    def test_registry_event_consumer(self, test_deployments_service, test_session_factory):
        pass
