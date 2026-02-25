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
    validate_response_bad_request,
)


class TestInitiateDeployment:
    def test_initiate_deployment_only_daemon_ok(
        self,
        test_deployments_service,
        test_auth_service,
        test_org_id,
        test_service_id,
        test_service_endpoint,
        test_service_credentials,
    ):
        event = generate_request_event(
            body={
                "orgId": test_org_id,
                "serviceId": test_service_id,
                "onlyDaemon": True,
                "serviceEndpoint": test_service_endpoint,
                "serviceCredentials": test_service_credentials,
            }
        )

        response = initiate_deployment(
            event, None, test_deployments_service, auth_service=test_auth_service
        )
        _, data = validate_response_ok(response)

        assert data["orgId"] == test_org_id
        assert data["serviceId"] == test_service_id
        assert data["daemon"]["status"] == DaemonStatus.INIT.value
        assert data["daemon"]["daemonConfig"]["serviceEndpoint"] == test_service_endpoint
        assert data["daemon"]["daemonConfig"]["serviceCredentials"] == test_service_credentials
        assert not data["daemon"]["daemonConfig"]["isServiceHosted"]
        assert data["daemon"]["daemonEndpoint"] == test_deployments_service._get_daemon_endpoint(
            test_org_id, test_service_id
        )
        assert data["hostedService"] is None

    def test_initiate_deployment_daemon_and_service_ok(
        self,
        test_deployments_service,
        test_auth_service,
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
        assert data["daemon"]["daemonConfig"]["isServiceHosted"]
        assert data["daemon"]["daemonEndpoint"] == test_deployments_service._get_daemon_endpoint(
            test_org_id, test_service_id
        )
        assert data["hostedService"]["status"] == HostedServiceStatus.INIT.value
        assert data["hostedService"]["githubAccountName"] == test_account
        assert data["hostedService"]["githubRepositoryName"] == test_repo
        assert data["hostedService"]["lastCommitUrl"] == ""

    def test_initiate_deployment_add_service_ok(
        self,
        test_deployments_service,
        test_auth_service,
        add_test_daemon,
        test_org_id,
        test_service_id,
        test_daemon_id,
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
        assert data["daemon"]["status"] == DaemonStatus.UP.value
        assert data["daemon"]["id"] == test_daemon_id
        assert data["daemon"]["daemonConfig"]["serviceEndpoint"] == ""
        assert data["daemon"]["daemonConfig"]["isServiceHosted"]
        assert data["hostedService"]["status"] == HostedServiceStatus.INIT.value
        assert data["hostedService"]["githubAccountName"] == test_account
        assert data["hostedService"]["githubRepositoryName"] == test_repo
        assert data["hostedService"]["lastCommitUrl"] == ""

    def test_initiate_deployment_only_daemon_already_exists(
        self,
        test_deployments_service,
        test_auth_service,
        add_test_daemon,
        test_org_id,
        test_service_id,
        test_service_endpoint,
        test_service_credentials,
    ):
        event = generate_request_event(
            body={
                "orgId": test_org_id,
                "serviceId": test_service_id,
                "onlyDaemon": True,
                "serviceEndpoint": test_service_endpoint,
                "serviceCredentials": test_service_credentials,
            }
        )

        response = initiate_deployment(
            event, None, test_deployments_service, auth_service=test_auth_service
        )
        _, message = validate_response_bad_request(response)

        assert (
            message
            == f"Daemon for service with org_id={test_org_id} and service_id={test_service_id} already exists!"
        )

    def test_initiate_deployment_daemon_and_service_already_exists(
        self,
        test_deployments_service,
        test_auth_service,
        add_test_daemon_and_service,
        test_org_id,
        test_service_id,
    ):
        event = generate_request_event(
            body={
                "orgId": test_org_id,
                "serviceId": test_service_id,
                "onlyDaemon": False,
                "githubAccountName": "qwe",
                "githubRepositoryName": "rty",
            }
        )

        response = initiate_deployment(
            event, None, test_deployments_service, auth_service=test_auth_service
        )
        _, message = validate_response_bad_request(response)

        assert (
            message
            == f"Daemon and hosted service for service with org_id={test_org_id} and service_id={test_service_id} already exist!"
        )

    def test_initiate_deployment_incorrect_credentials_format(
        self,
        test_deployments_service,
        test_auth_service,
        test_org_id,
        test_service_id,
        test_service_endpoint,
        test_service_credentials,
    ):
        test_service_credentials[0]["key"] = ""

        event = generate_request_event(
            body={
                "orgId": test_org_id,
                "serviceId": test_service_id,
                "onlyDaemon": True,
                "serviceEndpoint": test_service_endpoint,
                "serviceCredentials": test_service_credentials,
            }
        )

        response = initiate_deployment(
            event, None, test_deployments_service, auth_service=test_auth_service
        )
        _, message = validate_response_bad_request(response)

        assert (
            message
            == "Invalid service auth parameters! Must be 'key', 'value' and 'location' and not empty."
        )

    def test_initiate_deployment_missing_service_endpoint(
        self,
        test_deployments_service,
        test_auth_service,
        test_org_id,
        test_service_id,
        test_service_credentials,
    ):
        event = generate_request_event(
            body={
                "orgId": test_org_id,
                "serviceId": test_service_id,
                "onlyDaemon": True,
                "serviceEndpoint": "",
                "serviceCredentials": test_service_credentials,
            }
        )

        response = initiate_deployment(
            event, None, test_deployments_service, auth_service=test_auth_service
        )
        _, message = validate_response_bad_request(response)

        assert message == "Missing service endpoint!"

    def test_initiate_deployment_missing_github_parameters(
        self,
        test_deployments_service,
        test_auth_service,
        test_org_id,
        test_service_id,
    ):
        event = generate_request_event(
            body={
                "orgId": test_org_id,
                "serviceId": test_service_id,
                "onlyDaemon": False,
                "githubAccountName": "qwe",
                "githubRepositoryName": "",
            }
        )

        response = initiate_deployment(
            event, None, test_deployments_service, auth_service=test_auth_service
        )
        _, message = validate_response_bad_request(response)

        assert message == "Missing github account name or repository name!"


class TestGetUserDeployments:
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

    def test_get_user_deployments_no_deployments_ok(self, test_deployments_service):
        response = get_user_deployments(None, None, test_deployments_service)
        _, data = validate_response_ok(response)

        assert len(data) == 0


class TestSearchDeployments:
    def test_search_deployments_daemon_and_service_ok(
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

    def test_search_deployments_only_daemon_ok(
        self,
        test_deployments_service,
        test_auth_service,
        add_test_daemon,
        test_org_id,
        test_service_id,
        test_daemon_id,
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
        assert data["hostedService"] is None
        assert data["accountsMatch"]

    def test_search_deployments_no_deployments_ok(
        self,
        test_deployments_service,
        test_auth_service,
        test_org_id,
        test_service_id,
        test_daemon_id,
    ):
        event = generate_request_event(
            query_parameters={"orgId": test_org_id, "serviceId": test_service_id}
        )

        response = search_deployments(event, None, test_deployments_service, test_auth_service)
        _, data = validate_response_ok(response)

        assert data == {"daemon": None, "hostedService": None}


class TestGetPublicKey:
    def test_get_public_key_ok(self, test_deployments_service):
        response = get_public_key(None, None, test_deployments_service)
        _, data = validate_response_ok(response)

        assert data["publicKey"] == "PUBLIC_KEY"


class TestRegistryEventConsumer:
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
