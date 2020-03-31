from unittest import TestCase
from datetime import datetime as dt
from registry.application.handlers.slack_chat_operation_handler import get_list_of_service_pending_for_approval
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository
from registry.infrastructure.models import Service as ServiceDBModel, ServiceState as ServiceStateDBModel,\
    Organization as OrganizationDBModel, OrganizationState as OrganizationStateDBModel
from registry.domain.models.organization import Organization as OrganizationDomainModel
from registry.constants import OrganizationStatus, ServiceStatus
from unittest.mock import patch
org_repo = OrganizationPublisherRepository()
service_repo = ServicePublisherRepository()


class TestSlackChatOperation(TestCase):
    def setUp(self):
        pass

    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_user")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_channel_id")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_signature")
    @patch("registry.application.services.slack_chat_operation.requests.post")
    def test_get_list_of_service_pending_for_approval(self, post_request, validate_slack_signature, validate_slack_channel_id, validate_slack_user):
        validate_slack_channel_id.return_value = True
        validate_slack_user.return_value = True
        validate_slack_signature.return_value = True
        post_request.return_value = {}
        self.tearDown()
        org_repo.add_organization(
            OrganizationDomainModel(
                "test_org_uuid", "test_org_id", "org_dummy", "ORGANIZATION", "PUBLISHER", "description",
                "short_description", "https://test.io", [], {}, "ipfs_hash", "123456879", [], [], [], []),
            "dummy", OrganizationStatus.PUBLISHED.value)
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid_1",
                display_name="test_display_name_1",
                service_id="test_service_id_1",
                metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                ranking=1,
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid_2",
                display_name="test_display_name_2",
                service_id="test_service_id_2",
                metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                ranking=1,
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceStateDBModel(
                row_id=1000,
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid_1",
                state=ServiceStatus.APPROVAL_PENDING.value,
                transaction_hash=None,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceStateDBModel(
                row_id=1001,
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid_2",
                state=ServiceStatus.APPROVAL_PENDING.value,
                transaction_hash=None,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )
        event = {
            'resource': '/services',
            'path': '/services',
            'httpMethod': 'POST',
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'mu1l28rgji.execute-api.us-east-1.amazonaws.com',
                'X-Slack-Request-Timestamp': '1585592248',
                'X-Slack-Signature': 'v0=2f1e3b11bd3758d159971da4f0c2fe4569757a5ebb7991a48f84ee19cbfd7725'
            },
            'queryStringParameters': None,
            'requestContext': {},
            'body': 'token=HiVKf04RB8GV6bmaaBqx7nAr&team_id=T996H7VS8&team_domain=snet&channel_id=GSR47N62X&channel_name=privategroup&user_id=UE8CNNEGZ&user_name=prashant&command=%2Flist-orgs-for-approval&text=&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT996H7VS8%2F1026304454785%2F1usQbPB0kRIGjdhUifXDLSu2&trigger_id=1026304454913.315221267892.794872083bae86aa00c776ba3bc74b30',
            'isBase64Encoded': False
        }
        response = get_list_of_service_pending_for_approval(event, context=None)
        print(response)

    def tearDown(self):
        org_repo.session.query(OrganizationDBModel).delete()
        org_repo.session.query(OrganizationStateDBModel).delete()
        org_repo.session.query(ServiceDBModel).delete()
        org_repo.session.query(ServiceStateDBModel).delete()
