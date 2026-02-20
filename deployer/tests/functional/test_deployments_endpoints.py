from deployer.application.handlers.deployments_handlers import (
    initiate_deployment,
    get_user_deployments,
    search_deployments,
    get_public_key,
    registry_event_consumer,
)
from deployer.infrastructure.db import session_scope
from deployer.infrastructure.models import DaemonStatus, HostedServiceStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.tests.functional.utils import (
    generate_request_event,
    validate_response_ok,
    create_common_queue_event,
)


class TestInitiateDeployment:
    def test_initiate_deployment_only_daemon_ok(
        self,
        test_deployments_service,
        test_auth_service,
        test_session_factory,
        test_org_id,
        test_service_id,
    ):
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
                "serviceCredentials": test_credentials,
            }
        )

        response = initiate_deployment(
            event, None, test_deployments_service, auth_service=test_auth_service
        )
        _, data = validate_response_ok(response)

        assert data["orgId"] == test_org_id
        assert data["serviceId"] == test_service_id
        assert data["daemon"]["status"] == DaemonStatus.INIT.value
        assert data["daemon"]["daemonConfig"]["serviceEndpoint"] == test_endpoint
        assert data["daemon"]["daemonConfig"]["serviceCredentials"] == test_credentials
        assert data["daemon"]["daemonEndpoint"] == test_deployments_service._get_daemon_endpoint(
            test_org_id, test_service_id
        )
        assert data["hostedService"] is None

    def test_initiate_deployment_ok(
        self,
        test_deployments_service,
        test_auth_service,
        test_session_factory,
        test_org_id,
        test_service_id,
    ):
        test_account = "qwe"
        test_repo = "rty"

        event = generate_request_event(
            body={
                "orgId": test_org_id,
                "serviceId": test_service_id,
                "onlyDaemon": False,
                "githubAccountName": test_account,
                "githubRepositoryName": test_repo,
            }
        )

        response = initiate_deployment(
            event, None, test_deployments_service, auth_service=test_auth_service
        )
        _, data = validate_response_ok(response)

        assert data["orgId"] == test_org_id
        assert data["serviceId"] == test_service_id
        assert data["daemon"]["status"] == DaemonStatus.INIT.value
        assert data["daemon"]["daemonConfig"]["serviceEndpoint"] == ""
        assert data["daemon"]["daemonEndpoint"] == test_deployments_service._get_daemon_endpoint(
            test_org_id, test_service_id
        )
        assert data["hostedService"]["status"] == HostedServiceStatus.INIT.value
        assert data["hostedService"]["githubAccountName"] == test_account
        assert data["hostedService"]["githubRepositoryName"] == test_repo
        assert data["hostedService"]["lastCommitUrl"] == ""


class TestDeploymentsEndpoints:
    def test_get_user_deployments_ok(
        self,
        test_deployments_service,
        add_test_daemon_and_service,
        add_test_daemon,
        test_org_id,
        test_service_id,
        test_daemon_id,
        test_hosted_service_id,
    ):
        response = get_user_deployments(None, None, test_deployments_service)
        _, data = validate_response_ok(response)

        assert len(data) == 2
        if data[0]["hostedService"] is not None:
            full_deployment = data[0]
            short_deployment = data[1]
        else:
            full_deployment = data[1]
            short_deployment = data[0]

        assert full_deployment["orgId"] == test_org_id
        assert full_deployment["serviceId"] == test_service_id
        assert full_deployment["daemon"]["id"] == test_daemon_id
        assert full_deployment["daemon"]["status"] == DaemonStatus.UP.value
        assert full_deployment["hostedService"]["id"] == test_hosted_service_id
        assert full_deployment["hostedService"]["status"] == HostedServiceStatus.UP.value

        assert short_deployment["orgId"] == f"{test_org_id}_2"
        assert short_deployment["serviceId"] == f"{test_service_id}_2"
        assert short_deployment["daemon"]["id"] == f"{test_daemon_id}_2"
        assert short_deployment["daemon"]["status"] == DaemonStatus.UP.value
        assert short_deployment["hostedService"] is None

    def test_search_deployments_ok(
        self,
        test_deployments_service,
        test_auth_service,
        add_test_daemon_and_service,
        test_org_id,
        test_service_id,
        test_daemon_id,
        test_hosted_service_id,
    ):
        event = generate_request_event(
            query_parameters={"orgId": test_org_id, "serviceId": test_service_id}
        )

        response = search_deployments(event, None, test_deployments_service, test_auth_service)
        _, data = validate_response_ok(response)

        assert data["orgId"] == test_org_id
        assert data["serviceId"] == test_service_id
        assert data["daemon"]["id"] == test_daemon_id
        assert data["daemon"]["status"] == DaemonStatus.UP.value
        assert data["daemon"]["daemonConfig"] == {}
        assert data["daemon"]["daemonEndpoint"] == ""
        assert data["hostedService"]["id"] == test_hosted_service_id
        assert data["hostedService"]["status"] == HostedServiceStatus.UP.value
        assert data["hostedService"]["githubAccountName"] == ""
        assert data["hostedService"]["githubRepositoryName"] == ""
        assert data["hostedService"]["lastCommitUrl"] == ""
        assert data["accountsMatch"]

    def test_get_public_key_ok(self, test_deployments_service):
        response = get_public_key(None, None, test_deployments_service)
        _, data = validate_response_ok(response)

        assert data["publicKey"] == "PUBLIC_KEY"

    def test_registry_event_consumer_service_metadata_modified_ok(
        self,
        test_deployments_service,
        test_session_factory,
        add_test_daemon_and_service,
        test_org_id,
        test_service_id,
        test_daemon_id,
    ):
        group_name = "default_group"
        service_class = "example_service"

        test_event = create_common_queue_event(
            [
                {
                    "blockchain_event": {
                        "name": "ServiceMetadataModified",
                        "data": {
                            "json_str": "{'orgId': b'TEST_ORG_ID\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'serviceId': b'TEST_SERVICE_ID\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'metadataURI': b'ipfs://QmNScVpiGismK2x2ZahFiPTKUXgS21GpciKSexmPf3Hej6\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}"  # real uri to test work with metadata
                        },
                    }
                }
            ]
        )

        registry_event_consumer(test_event, None, test_deployments_service)

        with session_scope(test_session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, test_daemon_id)

        assert daemon.daemon_config["daemon_group"] == group_name
        assert daemon.daemon_config["service_class"] == service_class
