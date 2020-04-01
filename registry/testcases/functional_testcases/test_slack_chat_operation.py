from unittest import TestCase
from datetime import datetime as dt
from registry.application.handlers.slack_chat_operation_handler import get_list_of_service_pending_for_approval, \
    slack_interaction_handler
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository
from registry.infrastructure.models import Service as ServiceDBModel, ServiceState as ServiceStateDBModel, \
    Organization as OrganizationDBModel, OrganizationState as OrganizationStateDBModel
from registry.domain.models.organization import Organization as OrganizationDomainModel
from registry.constants import OrganizationStatus, ServiceStatus
from unittest.mock import patch

org_repo = OrganizationPublisherRepository()
service_repo = ServicePublisherRepository()


class TestSlackChatOperation(TestCase):
    def setUp(self):
        pass

    # @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_user")
    # @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_channel_id")
    # @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_signature")
    # @patch("registry.application.services.slack_chat_operation.requests.post")
    # def test_get_list_of_service_pending_for_approval(self, post_request, validate_slack_signature,
    #                                                   validate_slack_channel_id, validate_slack_user):
    #     validate_slack_channel_id.return_value = True
    #     validate_slack_user.return_value = True
    #     validate_slack_signature.return_value = True
    #     post_request.return_value.status_code = 200
    #     post_request.return_value.text = ""
    #     self.tearDown()
    #     org_repo.add_organization(
    #         OrganizationDomainModel(
    #             "test_org_uuid", "test_org_id", "org_dummy", "ORGANIZATION", "PUBLISHER", "description",
    #             "short_description", "https://test.io", [], {}, "ipfs_hash", "123456879", [], [], [], []),
    #         "dummy", OrganizationStatus.PUBLISHED.value)
    #     service_repo.add_item(
    #         ServiceDBModel(
    #             org_uuid="test_org_uuid",
    #             uuid="test_service_uuid_1",
    #             display_name="test_display_name_1",
    #             service_id="test_service_id_1",
    #             metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
    #             short_description="test_short_description",
    #             description="test_description",
    #             project_url="https://dummy.io",
    #             ranking=1,
    #             created_on=dt.utcnow()
    #         )
    #     )
    #     service_repo.add_item(
    #         ServiceDBModel(
    #             org_uuid="test_org_uuid",
    #             uuid="test_service_uuid_2",
    #             display_name="test_display_name_2",
    #             service_id="test_service_id_2",
    #             metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
    #             short_description="test_short_description",
    #             description="test_description",
    #             project_url="https://dummy.io",
    #             ranking=1,
    #             created_on=dt.utcnow()
    #         )
    #     )
    #     service_repo.add_item(
    #         ServiceStateDBModel(
    #             row_id=1000,
    #             org_uuid="test_org_uuid",
    #             service_uuid="test_service_uuid_1",
    #             state=ServiceStatus.APPROVAL_PENDING.value,
    #             transaction_hash=None,
    #             created_by="dummy_user",
    #             updated_by="dummy_user",
    #             created_on=dt.utcnow()
    #         )
    #     )
    #     service_repo.add_item(
    #         ServiceStateDBModel(
    #             row_id=1001,
    #             org_uuid="test_org_uuid",
    #             service_uuid="test_service_uuid_2",
    #             state=ServiceStatus.APPROVAL_PENDING.value,
    #             transaction_hash=None,
    #             created_by="dummy_user",
    #             updated_by="dummy_user",
    #             created_on=dt.utcnow()
    #         )
    #     )
    #     event = {
    #         'resource': '/services',
    #         'path': '/services',
    #         'httpMethod': 'POST',
    #         'headers': {
    #             'Content-Type': 'application/x-www-form-urlencoded',
    #             'Host': 'mu1l28rgji.execute-api.us-east-1.amazonaws.com',
    #             'X-Slack-Request-Timestamp': '1585592248',
    #             'X-Slack-Signature': 'v0=2f1e3b11bd3758d159971da4f0c2fe4569757a5ebb7991a48f84ee19cbfd7725'
    #         },
    #         'queryStringParameters': None,
    #         'requestContext': {},
    #         'body': 'token=HiVKf04RB8GV6bmaaBqx7nAr&team_id=T996H7VS8&team_domain=snet&channel_id=GSR47N62X&channel_name=privategroup&user_id=UE8CNNEGZ&user_name=prashant&command=%2Flist-orgs-for-approval&text=&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT996H7VS8%2F1026304454785%2F1usQbPB0kRIGjdhUifXDLSu2&trigger_id=1026304454913.315221267892.794872083bae86aa00c776ba3bc74b30',
    #         'isBase64Encoded': False
    #     }
    #     response = get_list_of_service_pending_for_approval(event, context=None)
    #     assert (response["status_code"] == 200)

    # def test_get_service_details(self):
    #     event = {
    #         'resource': '/submit',
    #         'path': '/submit',
    #         'httpMethod': 'POST',
    #         'headers': {
    #             'Accept': 'application/json,*/*',
    #             'Content-Type': 'application/x-www-form-urlencoded',
    #             'X-Slack-Request-Timestamp': '1585689476',
    #             'X-Slack-Signature': 'v0=35d5897c89be85426dd326d159732505680b2f3595250da2e994df0d973406c2'
    #         },
    #         'queryStringParameters': None,
    #         'multiValueQueryStringParameters': None,
    #         'pathParameters': None,
    #         'stageVariables': None,
    #         'body': 'payload=%7B%22type%22%3A%22block_actions%22%2C%22team%22%3A%7B%22id%22%3A%22T996H7VS8%22%2C%22domain%22%3A%22snet%22%7D%2C%22user%22%3A%7B%22id%22%3A%22UE8CNNEGZ%22%2C%22username%22%3A%22prashant%22%2C%22name%22%3A%22prashant%22%2C%22team_id%22%3A%22T996H7VS8%22%7D%2C%22api_app_id%22%3A%22ATF2TALQM%22%2C%22token%22%3A%22HiVKf04RB8GV6bmaaBqx7nAr%22%2C%22container%22%3A%7B%22type%22%3A%22message%22%2C%22message_ts%22%3A%221585689470.002800%22%2C%22channel_id%22%3A%22CSR47N62X%22%2C%22is_ephemeral%22%3Afalse%7D%2C%22trigger_id%22%3A%221041739696663.315221267892.5d1e3803e21ef7376ec5ea2525feb0a4%22%2C%22channel%22%3A%7B%22id%22%3A%22CSR47N62X%22%2C%22name%22%3A%22privategroup%22%7D%2C%22message%22%3A%7B%22type%22%3A%22message%22%2C%22subtype%22%3A%22bot_message%22%2C%22text%22%3A%22This+content+can%27t+be+displayed.%22%2C%22ts%22%3A%221585689470.002800%22%2C%22bot_id%22%3A%22B0114DB6KU0%22%2C%22blocks%22%3A%5B%7B%22type%22%3A%22section%22%2C%22block_id%22%3A%22WPJsP%22%2C%22text%22%3A%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AService+Approval+Request%2A%22%2C%22verbatim%22%3Afalse%7D%7D%2C%7B%22type%22%3A%22section%22%2C%22block_id%22%3A%22zUs5Y%22%2C%22fields%22%3A%5B%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AService+Id%3A%2A%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2ARequested+on%3A%2A%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%3Chttp%3A%5C%2F%5C%2Fstaging-dapp.singularitynet.io.s3-website-us-east-1.amazonaws.com%5C%2Fservicedetails%7Cnew_service%3E%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22None%22%2C%22verbatim%22%3Afalse%7D%5D%7D%2C%7B%22type%22%3A%22actions%22%2C%22block_id%22%3A%22gwx4%22%2C%22elements%22%3A%5B%7B%22type%22%3A%22button%22%2C%22action_id%22%3A%22AFK0%22%2C%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Review%22%2C%22emoji%22%3Atrue%7D%2C%22style%22%3A%22primary%22%2C%22value%22%3A%22%7B%5C%22service_uuid%5C%22%3A+%5C%22abc%5C%22%2C+%5C%22path%5C%22%3A+%5C%22%5C%2Fservice%5C%22%7D%22%7D%5D%7D%2C%7B%22type%22%3A%22divider%22%2C%22block_id%22%3A%22twXk%22%7D%2C%7B%22type%22%3A%22section%22%2C%22block_id%22%3A%22DwN%22%2C%22fields%22%3A%5B%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AService+Id%3A%2A%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2ARequested+on%3A%2A%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%3Chttp%3A%5C%2F%5C%2Fstaging-dapp.singularitynet.io.s3-website-us-east-1.amazonaws.com%5C%2Fservicedetails%7Cnew_service%3E%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22None%22%2C%22verbatim%22%3Afalse%7D%5D%7D%2C%7B%22type%22%3A%22actions%22%2C%22block_id%22%3A%22c7zJ6%22%2C%22elements%22%3A%5B%7B%22type%22%3A%22button%22%2C%22action_id%22%3A%22A%3DHe%22%2C%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Review%22%2C%22emoji%22%3Atrue%7D%2C%22style%22%3A%22primary%22%2C%22value%22%3A%22https%3A%5C%2F%5C%2Fmu1l28rgji.execute-api.us-east-1.amazonaws.com%5C%2Ftest%5C%2Fsubmit%3Fservice_uuid%3Dzsd%22%7D%5D%7D%2C%7B%22type%22%3A%22divider%22%2C%22block_id%22%3A%22Bib%22%7D%5D%7D%2C%22response_url%22%3A%22https%3A%5C%2F%5C%2Fhooks.slack.com%5C%2Factions%5C%2FT996H7VS8%5C%2F1039654727429%5C%2FcOV3SyZOl4iTGJWzkadFfOVb%22%2C%22actions%22%3A%5B%7B%22action_id%22%3A%22AFK0%22%2C%22block_id%22%3A%22gwx4%22%2C%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Review%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22%7B%5C%22service_uuid%5C%22%3A+%5C%22abc%5C%22%2C+%5C%22path%5C%22%3A+%5C%22%5C%2Fservice%5C%22%7D%22%2C%22style%22%3A%22primary%22%2C%22type%22%3A%22button%22%2C%22action_ts%22%3A%221585689476.552357%22%7D%5D%7D',
    #         'isBase64Encoded': False
    #     }
    #     response = slack_interaction_handler(event=event, context=None)
    #     print(response)

    def test_view_submission(self):
        event = {
            'resource': '/submit',
            'path': '/submit',
            'httpMethod': 'POST',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Slack-Request-Timestamp': '1585689487',
                        'X-Slack-Signature': 'v0=9edac86d470f8b6a6106add4d6feae40b4e559e36ca84f32044f91cf159981ff'},
            'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': None,
            'stageVariables': None,
            'body': 'payload=%7B%22type%22%3A%22view_submission%22%2C%22team%22%3A%7B%22id%22%3A%22T996H7VS8%22%2C%22domain%22%3A%22snet%22%7D%2C%22user%22%3A%7B%22id%22%3A%22UE8CNNEGZ%22%2C%22username%22%3A%22prashant%22%2C%22name%22%3A%22prashant%22%2C%22team_id%22%3A%22T996H7VS8%22%7D%2C%22api_app_id%22%3A%22ATF2TALQM%22%2C%22token%22%3A%22HiVKf04RB8GV6bmaaBqx7nAr%22%2C%22trigger_id%22%3A%221041592548150.315221267892.9396ecf1cc0393f4c0688cbc317fe9b0%22%2C%22view%22%3A%7B%22id%22%3A%22V0117HE5L3G%22%2C%22team_id%22%3A%22T996H7VS8%22%2C%22type%22%3A%22modal%22%2C%22blocks%22%3A%5B%7B%22type%22%3A%22section%22%2C%22block_id%22%3A%22rK2B%22%2C%22fields%22%3A%5B%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AOrganization+Id%3A%2A%5Cnalphabet%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AOrganization+Name%3A%2A%5CnAlphabet%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AService+Id%3A%2A%5Cndeepmind%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AService+Name%3A%2A%5CnDeep+Mind%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AApproval+Platform%3A%2A%5Cn%3Chttp%3A%5C%2F%5C%2Fstaging-dapp.singularitynet.io.s3-website-us-east-1.amazonaws.com%3E%5Cn%22%2C%22verbatim%22%3Afalse%7D%2C%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AWhen%3A%2A%5CnMar10%2C+2020+%2816+Days+before%29%5Cn%22%2C%22verbatim%22%3Afalse%7D%5D%7D%2C%7B%22type%22%3A%22divider%22%2C%22block_id%22%3A%2297BF%22%7D%2C%7B%22type%22%3A%22actions%22%2C%22block_id%22%3A%22qVvl6%22%2C%22elements%22%3A%5B%7B%22type%22%3A%22button%22%2C%22action_id%22%3A%22%5C%2FPD1%22%2C%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Approve%22%2C%22emoji%22%3Atrue%7D%2C%22style%22%3A%22primary%22%2C%22value%22%3A%22https%3A%5C%2F%5C%2Fmu1l28rgji.execute-api.us-east-1.amazonaws.com%5C%2Ftest%5C%2Fsubmit%22%7D%2C%7B%22type%22%3A%22button%22%2C%22action_id%22%3A%22wrB8K%22%2C%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Reject%22%2C%22emoji%22%3Atrue%7D%2C%22style%22%3A%22danger%22%2C%22value%22%3A%22click_me_123%22%7D%5D%7D%2C%7B%22type%22%3A%22section%22%2C%22block_id%22%3A%22CwJ%22%2C%22text%22%3A%7B%22type%22%3A%22mrkdwn%22%2C%22text%22%3A%22%2AApprove+%5C%2F+Reject+%5C%2F+Request+Change%2A%22%2C%22verbatim%22%3Afalse%7D%2C%22accessory%22%3A%7B%22type%22%3A%22radio_buttons%22%2C%22initial_option%22%3A%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Approve%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22Approve%22%7D%2C%22options%22%3A%5B%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Approve%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22Approve%22%7D%2C%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Reject%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22Reject%22%7D%2C%7B%22text%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Request+Change%22%2C%22emoji%22%3Atrue%7D%2C%22value%22%3A%22Request+Change%22%7D%5D%2C%22action_id%22%3A%22P5fX%22%7D%7D%2C%7B%22type%22%3A%22input%22%2C%22block_id%22%3A%22e8sOA%22%2C%22label%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Comment%22%2C%22emoji%22%3Atrue%7D%2C%22hint%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22%2A+Comment+is+mandatory+for+Reject+and+Request+Change%22%2C%22emoji%22%3Atrue%7D%2C%22optional%22%3Afalse%2C%22element%22%3A%7B%22type%22%3A%22plain_text_input%22%2C%22multiline%22%3Atrue%2C%22action_id%22%3A%229C3p%22%7D%7D%5D%2C%22private_metadata%22%3A%22%22%2C%22callback_id%22%3A%22%22%2C%22state%22%3A%7B%22values%22%3A%7B%22e8sOA%22%3A%7B%229C3p%22%3A%7B%22type%22%3A%22plain_text_input%22%2C%22value%22%3A%22approved%22%7D%7D%7D%7D%2C%22hash%22%3A%221585689476.09fee1c2%22%2C%22title%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Services+For+Approval%22%2C%22emoji%22%3Atrue%7D%2C%22clear_on_close%22%3Afalse%2C%22notify_on_close%22%3Afalse%2C%22close%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Cancel%22%2C%22emoji%22%3Atrue%7D%2C%22submit%22%3A%7B%22type%22%3A%22plain_text%22%2C%22text%22%3A%22Request+For+Changes%22%2C%22emoji%22%3Atrue%7D%2C%22previous_view_id%22%3Anull%2C%22root_view_id%22%3A%22V0117HE5L3G%22%2C%22app_id%22%3A%22ATF2TALQM%22%2C%22external_id%22%3A%22%22%2C%22app_installed_team_id%22%3A%22T996H7VS8%22%2C%22bot_id%22%3A%22B010N18ND7E%22%7D%2C%22response_urls%22%3A%5B%5D%7D',
            'isBase64Encoded': False
        }
        response = slack_interaction_handler(event=event, context=None)
        print(response)

    def tearDown(self):
        org_repo.session.query(OrganizationDBModel).delete()
        org_repo.session.query(OrganizationStateDBModel).delete()
        org_repo.session.query(ServiceDBModel).delete()
        org_repo.session.query(ServiceStateDBModel).delete()
