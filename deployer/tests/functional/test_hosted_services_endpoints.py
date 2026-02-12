from common.logger import get_logger
from deployer.application.handlers.hosted_services_handlers import (
    get_hosted_service,
    check_github_repository,
    get_hosted_service_logs,
    update_hosted_service_status,
)
from deployer.infrastructure.db import session_scope
from deployer.infrastructure.models import HostedServiceStatus
from deployer.infrastructure.repositories.hosted_service_repository import HostedServiceRepository
from deployer.tests.functional.utils import (
    generate_request_event,
    validate_response_ok,
    create_common_queue_event,
)

logger = get_logger(__name__)


class TestHostedServicesEndpoints:
    def test_get_hosted_service_ok(
        self,
        test_hosted_services_service,
        test_auth_service,
        add_test_daemon_and_service,
        test_org_id,
        test_service_id,
        test_hosted_service_id,
    ):
        event = generate_request_event(path_parameters={"hostedServiceId": test_hosted_service_id})

        response = get_hosted_service(event, None, test_hosted_services_service, test_auth_service)
        _, data = validate_response_ok(response)

        assert data["orgId"] == test_org_id
        assert data["serviceId"] == test_service_id
        assert data["id"] == test_hosted_service_id
        assert data["status"] == HostedServiceStatus.UP.value
        assert data["githubAccountName"] == ""
        assert data["githubRepositoryName"] == ""
        assert data["lastCommitUrl"] == ""

    def test_check_github_repository_true_ok(self, test_hosted_services_service):
        test_hosted_services_service._github_api_client.is_installed = True

        event = generate_request_event(
            query_parameters={"accountName": "test_account", "repositoryName": "test_repo"}
        )

        response = check_github_repository(event, None, test_hosted_services_service)
        _, data = validate_response_ok(response)

        assert data["isInstalled"]

    def test_check_github_repository_false_ok(self, test_hosted_services_service):
        test_hosted_services_service._github_api_client.is_installed = False

        event = generate_request_event(
            query_parameters={"accountName": "test_account", "repositoryName": "test_repository"}
        )

        response = check_github_repository(event, None, test_hosted_services_service)
        _, data = validate_response_ok(response)

        assert not data["isInstalled"]
        test_message = (
            "The application is not installed in the repository with "
            "account name test_account and repository name "
            "test_repository, or the account and/or repository "
            "name does not exist"
        )
        assert data["message"] == test_message

    def test_get_hosted_service_logs_ok(
        self,
        test_hosted_services_service,
        test_auth_service,
        add_test_daemon_and_service,
        test_hosted_service_id,
    ):
        event = generate_request_event(path_parameters={"hostedServiceId": test_hosted_service_id})

        response = get_hosted_service_logs(
            event, None, test_hosted_services_service, test_auth_service
        )
        _, data = validate_response_ok(response)

        assert data == ["log1", "log2", "log3"]

    def test_update_hosted_service_status_ok(
        self,
        test_hosted_services_service,
        test_session_factory,
        add_test_daemon_and_service,
        test_org_id,
        test_service_id,
        test_hosted_service_id,
    ):
        test_status = "VALIDATING"
        test_commit = "TEST_COMMIT_HASH"

        event = generate_request_event(
            orgId=test_org_id, serviceId=test_service_id, status=test_status, commit=test_commit
        )
        queue_event = create_common_queue_event([event])
        update_hosted_service_status(queue_event, None, test_hosted_services_service)

        with session_scope(test_session_factory) as session:
            hosted_service = HostedServiceRepository.get_hosted_service(
                session, test_hosted_service_id
            )

        assert hosted_service.status.value == test_status
        assert (
            hosted_service.last_commit_url
            == test_hosted_services_service._github_api_client.make_commit_url(
                hosted_service.github_account_name,
                hosted_service.github_repository_name,
                test_commit,
            )
        )
