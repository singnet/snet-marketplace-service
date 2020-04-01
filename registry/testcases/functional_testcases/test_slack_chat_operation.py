from unittest import TestCase
from datetime import datetime as dt
from registry.application.handlers.slack_chat_operation_handler import get_list_of_service_pending_for_approval, \
    slack_interaction_handler
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository
from registry.infrastructure.models import Service as ServiceDBModel, ServiceState as ServiceStateDBModel, \
    Organization as OrganizationDBModel, OrganizationState as OrganizationStateDBModel, ServiceComment as ServiceCommentDBModel
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
    def test_get_list_of_service_pending_for_approval(self, post_request, validate_slack_signature,
                                                      validate_slack_channel_id, validate_slack_user):
        validate_slack_channel_id.return_value = True
        validate_slack_user.return_value = True
        validate_slack_signature.return_value = True
        post_request.return_value.status_code = 200
        post_request.return_value.text = ""
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
        assert (response["statusCode"] == 200)

    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_user")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_channel_id")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_signature")
    @patch("registry.application.services.slack_chat_operation.requests.post")
    def test_slack_interaction_handler_to_view_service_modal(self, post_request, validate_slack_signature, validate_slack_channel_id, validate_slack_user):
        validate_slack_channel_id.return_value = True
        validate_slack_user.return_value = True
        validate_slack_signature.return_value = True
        post_request.return_value.status_code = 200
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
        event = {'resource': '/submit', 'path': '/submit', 'httpMethod': 'POST', 'headers': {'Accept': 'application/json,*/*', 'Accept-Encoding': 'gzip,deflate', 'Content-Type': 'application/x-www-form-urlencoded', 'Host': 'mu1l28rgji.execute-api.us-east-1.amazonaws.com', 'User-Agent': 'Slackbot 1.0 (+https://api.slack.com/robots)', 'X-Amzn-Trace-Id': 'Root=1-5e848305-176ba4c1ddcc311287ac49ce', 'X-Forwarded-For': '54.85.48.10', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https', 'X-Slack-Request-Timestamp': '1585742597', 'X-Slack-Signature': 'v0=5096314f4b78b0b75366d8429a5195ea01c7e67f5618ee05f8e94a94953e05fd'}, 'multiValueHeaders': {'Accept': ['application/json,*/*'], 'Accept-Encoding': ['gzip,deflate'], 'Content-Type': ['application/x-www-form-urlencoded'], 'Host': ['mu1l28rgji.execute-api.us-east-1.amazonaws.com'], 'User-Agent': ['Slackbot 1.0 (+https://api.slack.com/robots)'], 'X-Amzn-Trace-Id': ['Root=1-5e848305-176ba4c1ddcc311287ac49ce'], 'X-Forwarded-For': ['54.85.48.10'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https'], 'X-Slack-Request-Timestamp': ['1585742597'], 'X-Slack-Signature': ['v0=5096314f4b78b0b75366d8429a5195ea01c7e67f5618ee05f8e94a94953e05fd']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': None, 'stageVariables': None, 'requestContext': {'resourceId': 'p3jrvf', 'resourcePath': '/submit', 'httpMethod': 'POST', 'extendedRequestId': 'KTlo3E88oAMFkYA=', 'requestTime': '01/Apr/2020:12:03:17 +0000', 'path': '/test/submit', 'accountId': '533793137436', 'protocol': 'HTTP/1.1', 'stage': 'test', 'domainPrefix': 'mu1l28rgji', 'requestTimeEpoch': 1585742597420, 'requestId': '725888b7-41d5-47e9-a045-01f363603e17', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '54.85.48.10', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'Slackbot 1.0 (+https://api.slack.com/robots)', 'user': None}, 'domainName': 'mu1l28rgji.execute-api.us-east-1.amazonaws.com', 'apiId': 'mu1l28rgji'}, 'body': 'payload=%7B%22type%22%3A%22block_actions%22%2C%22team%22%3A%7B%22id%22%3A%22T996H7VS8%22%2C%22domain%22%3A%22snet%22%7D%2C%22user%22%3A%7B%22id%22%3A%22UE8CNNEGZ%22%2C%22username%22%3A%22prashant%22%2C%22name%22%3A%22prashant%22%2C%22team_id%22%3A%22T996H7VS8%22%7D%2C%22api_app_id%22%3A%22ATF2TALQM%22%2C%22token%22%3A%22HiVKf04RB8GV6bmaaBqx7nAr%22%2C%22container%22%3A%7B%22type%22%3A%22message%22%2C%22message_ts%22%3A%221585742592.001700%22%2C%22channel_id%22%3A%22CSR47N62X%22%2C%22is_ephemeral%22%3Afalse%7D%2C%22trigger_id%22%3A%221028338009186.315221267892.83550c5f247eb73b0ad743511e8698a6%22%2C%22channel%22%3A%7B%22id%22%3A%22CSR47N62X%22%2C%22name%22%3A%22privategroup%22%7D%2C%22message%22%3A%7B%22type%22%3A%22message%22%2C%22subtype%22%3A%22bot_message%22%2C%22text%22%3A%22This+content+can%27t+be+displayed.%22%2C%22ts%22%3A%221585742592.001700%22%2C%22bot_id%22%3A%22B0114DB6KU0%22%2C%22blocks%22%3A%5B%7B%22type%22%3A%22section%22%2C%22block_id%22%3A%22%2Bupe%22%2C%22text%22%3A%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AService+Approval+Request%2A%22%2C%22verbatim%22%3Afalse%7D%7D%2C%7B%22type%22%3A%22section%22%2C%22block_id%22%3A%22JjjW1%22%2C%22fields%22%3A%5B%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AService+Id%3A%2A%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2ARequested+on%3A%2A%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%3Chttp%3A%5C%2F%5C%2Fstaging-dapp.singularitynet.io.s3-website-us-east-1.amazonaws.com%5C%2Fservicedetails%7Cnew_service%3E%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22None%22%2C%22verbatim%22%3Afalse%7D%5D%7D%2C%7B%22type%22%3A%22actions%22%2C%22block_id%22%3A%22NJ0wG%22%2C%22elements%22%3A%5B%7B%22type%22%3A%22button%22%2C%22action_id%22%3A%22review%22%2C%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Review%22%2C%22emoji%22%3Atrue%7D%2C%22style%22%3A%22primary%22%2C%22value%22%3A%22%7B%5C%22org_id%5C%22%3A%5C%22test_org_id%5C%22%2C+%5C%22service_id%5C%22%3A+%5C%22test_service_id_1%5C%22%2C+%5C%22path%5C%22%3A+%5C%22%5C%2Fservice%5C%22%7D%22%7D%5D%7D%2C%7B%22type%22%3A%22divider%22%2C%22block_id%22%3A%22z3U%22%7D%5D%7D%2C%22response_url%22%3A%22https%3A%5C%2F%5C%2Fhooks.slack.com%5C%2Factions%5C%2FT996H7VS8%5C%2F1041051506757%5C%2FS4JIrJ2c7Bp0adma0EVeLXIV%22%2C%22actions%22%3A%5B%7B%22action_id%22%3A%22review%22%2C%22block_id%22%3A%22NJ0wG%22%2C%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Review%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22%7B%5C%22org_id%5C%22%3A%5C%22test_org_id%5C%22%2C+%5C%22service_id%5C%22%3A+%5C%22test_service_id_1%5C%22%2C+%5C%22path%5C%22%3A+%5C%22%5C%2Fservice%5C%22%7D%22%2C%22style%22%3A%22primary%22%2C%22type%22%3A%22button%22%2C%22action_ts%22%3A%221585742597.398302%22%7D%5D%7D', 'isBase64Encoded': False}
        response = slack_interaction_handler(event=event, context=None)
        print(response)

    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_user")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_channel_id")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_signature")
    def test_view_submission(self, validate_slack_signature, validate_slack_channel_id, validate_slack_user):
        validate_slack_channel_id.return_value = True
        validate_slack_user.return_value = True
        validate_slack_signature.return_value = True
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
        event = {
            'resource': '/submit',
            'path': '/submit',
            'httpMethod': 'POST',
            'headers': {'Accept': 'application/json,*/*',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Slack-Request-Timestamp': '1585737114',
                        'X-Slack-Signature': 'v0=5f52fbfa5a80733a0c7d9cad29dc69b452c402ad314e3409202a7b58f478461d'},
            'body': 'payload=%7B%22type%22%3A%22view_submission%22%2C%22team%22%3A%7B%22id%22%3A%22T996H7VS8%22%2C%22domain%22%3A%22snet%22%7D%2C%22user%22%3A%7B%22id%22%3A%22UE8CNNEGZ%22%2C%22username%22%3A%22prashant%22%2C%22name%22%3A%22prashant%22%2C%22team_id%22%3A%22T996H7VS8%22%7D%2C%22api_app_id%22%3A%22ATF2TALQM%22%2C%22token%22%3A%22HiVKf04RB8GV6bmaaBqx7nAr%22%2C%22trigger_id%22%3A%221042957767015.315221267892.fc7b53b0ce0f2d82c63b75e8b8600718%22%2C%22view%22%3A%7B%22id%22%3A%22V0118PTK36J%22%2C%22team_id%22%3A%22T996H7VS8%22%2C%22type%22%3A%22modal%22%2C%22blocks%22%3A%5B%7B%22type%22%3A%22section%22%2C%22block_id%22%3A%227Jh%22%2C%22fields%22%3A%5B%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AOrganization+Id%3A%2A%5Cntest_org_id%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AOrganization+Name%3A%2A%5Cnorg_dummy%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AService+Id%3A%2A%5Cntest_service_id_1%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AService+Name%3A%2A%5Cntest_display_name_1%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AApproval+Platform%3A%2A%5Cn%3Chttp%3A%5C%2F%5C%2Fstaging-dapp.singularitynet.io.s3-website-us-east-1.amazonaws.com%3E%5Cn%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AWhen%3A%2A%5CnMar10%2C+2020+%2816+Days+before%29%5Cn%22%2C%22verbatim%22%3Afalse%7D%5D%7D%2C%7B%22type%22%3A%22divider%22%2C%22block_id%22%3A%224Yw%22%7D%2C%7B%22type%22%3A%22actions%22%2C%22block_id%22%3A%22rQl3V%22%2C%22elements%22%3A%5B%7B%22type%22%3A%22button%22%2C%22action_id%22%3A%22rZhXe%22%2C%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Approve%22%2C%22emoji%22%3Atrue%7D%2C%22style%22%3A%22primary%22%2C%22value%22%3A%22https%3A%5C%2F%5C%2Fmu1l28rgji.execute-api.us-east-1.amazonaws.com%5C%2Ftest%5C%2Fsubmit%22%7D%2C%7B%22type%22%3A%22button%22%2C%22action_id%22%3A%22Wu4Rt%22%2C%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Reject%22%2C%22emoji%22%3Atrue%7D%2C%22style%22%3A%22danger%22%2C%22value%22%3A%22click_me_123%22%7D%5D%7D%2C%7B%22type%22%3A%22input%22%2C%22block_id%22%3A%22approval_state%22%2C%22label%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22%2AApprove+%5C%2F+Reject+%5C%2F+Request+Change%2A%22%2C%22emoji%22%3Atrue%7D%2C%22optional%22%3Afalse%2C%22element%22%3A%7B%22type%22%3A%22radio_buttons%22%2C%22action_id%22%3A%22selection%22%2C%22initial_option%22%3A%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Request+Change%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22CHANGE_REQUESTED%22%2C%22description%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Description+for+option+3%22%2C%22emoji%22%3Atrue%7D%7D%2C%22options%22%3A%5B%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Approve%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22APPROVED%22%2C%22description%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Description+for+option+1%22%2C%22emoji%22%3Atrue%7D%7D%2C%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Reject%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22REJECTED%22%2C%22description%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Description+for+option+2%22%2C%22emoji%22%3Atrue%7D%7D%2C%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Request+Change%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22CHANGE_REQUESTED%22%2C%22description%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Description+for+option+3%22%2C%22emoji%22%3Atrue%7D%7D%5D%7D%7D%2C%7B%22type%22%3A%22section%22%2C%22block_id%22%3A%22pm1z%22%2C%22text%22%3A%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AApprove+%5C%2F+Reject+%5C%2F+Request+Change%2A%22%2C%22verbatim%22%3Afalse%7D%2C%22accessory%22%3A%7B%22type%22%3A%22radio_buttons%22%2C%22initial_option%22%3A%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Approve%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22Approve%22%7D%2C%22options%22%3A%5B%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Approve%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22Approve%22%7D%2C%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Reject%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22Reject%22%7D%2C%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Request+Change%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22Request+Change%22%7D%5D%2C%22action_id%22%3A%22YRYc%22%7D%7D%2C%7B%22type%22%3A%22input%22%2C%22block_id%22%3A%22review_comment%22%2C%22label%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Comment%22%2C%22emoji%22%3Atrue%7D%2C%22hint%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22%2A+Comment+is+mandatory+for+Reject+and+Request+Change%22%2C%22emoji%22%3Atrue%7D%2C%22optional%22%3Afalse%2C%22element%22%3A%7B%22type%22%3A%22plain_text_input%22%2C%22action_id%22%3A%22comment%22%2C%22multiline%22%3Atrue%7D%7D%5D%2C%22private_metadata%22%3A%22%22%2C%22callback_id%22%3A%22%22%2C%22state%22%3A%7B%22values%22%3A%7B%22approval_state%22%3A%7B%22selection%22%3A%7B%22type%22%3A%22radio_buttons%22%2C%22selected_option%22%3A%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Reject%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22REJECTED%22%2C%22description%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Description+for+option+2%22%2C%22emoji%22%3Atrue%7D%7D%7D%7D%2C%22review_comment%22%3A%7B%22comment%22%3A%7B%22type%22%3A%22plain_text_input%22%2C%22value%22%3A%22service+has+missing+proto+files%22%7D%7D%7D%7D%2C%22hash%22%3A%221585737098.e7afa362%22%2C%22title%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Service+For+Approval%22%2C%22emoji%22%3Atrue%7D%2C%22clear_on_close%22%3Afalse%2C%22notify_on_close%22%3Afalse%2C%22close%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Cancel%22%2C%22emoji%22%3Atrue%7D%2C%22submit%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Submit%22%2C%22emoji%22%3Atrue%7D%2C%22previous_view_id%22%3Anull%2C%22root_view_id%22%3A%22V0118PTK36J%22%2C%22app_id%22%3A%22ATF2TALQM%22%2C%22external_id%22%3A%22%22%2C%22app_installed_team_id%22%3A%22T996H7VS8%22%2C%22bot_id%22%3A%22B010N18ND7E%22%7D%2C%22response_urls%22%3A%5B%5D%7D',
            'isBase64Encoded': False}
        response = slack_interaction_handler(event=event, context=None)
        assert (response["statusCode"] == 200)

    def tearDown(self):
        org_repo.session.query(OrganizationDBModel).delete()
        org_repo.session.query(OrganizationStateDBModel).delete()
        org_repo.session.query(ServiceDBModel).delete()
        org_repo.session.query(ServiceStateDBModel).delete()
        org_repo.session.query(ServiceCommentDBModel).delete()
