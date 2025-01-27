import json
from datetime import datetime as dt
from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

from registry.application.handlers.service_handlers import publish_service
from registry.constants import OrganizationMemberStatus
from registry.constants import Role
from registry.constants import ServiceStatus
from registry.infrastructure.models import OffchainServiceConfig as OffchainServiceConfigDBModel
from registry.infrastructure.models import Organization as OrganizationDBModel
from registry.infrastructure.models import OrganizationMember as OrganizationMemberDBModel
from registry.infrastructure.models import OrganizationState as OrganizationStateDBModel
from registry.infrastructure.models import Service as ServiceDBModel
from registry.infrastructure.models import ServiceGroup as ServiceGroupDBModel
from registry.infrastructure.models import ServiceReviewHistory as ServiceReviewHistoryDBModel
from registry.infrastructure.models import ServiceState as ServiceStateDBModel
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository

org_repo = OrganizationPublisherRepository()
service_repo = ServicePublisherRepository()


class TestServiceMetadata(TestCase):
    def setUp(self):
        self.tearDown()
        org_repo.add_item(
            OrganizationDBModel(
                name="test_org",
                org_id="test_org_id",
                uuid="test_org_uuid",
                org_type="organization",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                addresses=[],
                metadata_uri="#dummyhashdummyhash"
            )
        )
        new_org_members = [
            {
                "username": "karl@dummy.io",
                "address": "0x123"
            }
        ]
        org_repo.add_all_items(
            [
                OrganizationMemberDBModel(
                    username=member["username"],
                    org_uuid="test_org_uuid",
                    role=Role.MEMBER.value,
                    address=member["address"],
                    status=OrganizationMemberStatus.ACCEPTED.value,
                    transaction_hash="0x123",
                    invite_code=str(uuid4()),
                    invited_on=dt.utcnow(),
                    updated_on=dt.utcnow()
                ) for member in new_org_members
            ]
        )
        org_repo.add_item(
            OrganizationStateDBModel(
                org_uuid="test_org_uuid",
                state="APPROVED",
                created_by="karl@dummy.io",
                updated_by="karl@dummy.io"
            )
        )
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid",
                display_name="test_display_name",
                service_id="test_service_id",
                metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
                proto={"encoding": "proto", "service_type": "grpc",
                       "model_hash": "ipfs://QmcdTYvTxEJrv18Ui1vo1wNDisw8BMoFRMQyM13rz1ok5B"},
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                assets={"demo_files": {
                    "url": f"https://ropsten-marketplace-service-assets.s3.amazonaws.com/test_org_uuid/services/test_service_uuid/component/20210809094640_component.zip",
                    "status": "SUCCEEDED",
                    "required": "1",
                    "last_modified": "2020-08-18T00:10:20"
                }},
                rating={},
                ranking=1,
                contributors=[],
                mpe_address="#12345678",
                service_type="grpc", 
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceGroupDBModel(
                row_id="1000",
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid",
                group_id="test_group_id",
                pricing=[{"default": True, "price_model": "fixed_price", "price_in_cogs": 1}],
                endpoints={"https://dummydaemonendpoint.io": {"verfied": True}},
                daemon_address=["0xq2w3e4rr5t6y7u8i9"],
                free_calls=10,
                free_call_signer_address="0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F",
                group_name="default_group",
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            OffchainServiceConfigDBModel(
                row_id=10,
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid",
                parameter_name="demo_component_required",
                parameter_value=0,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceStateDBModel(
                row_id=1000,
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid",
                state=ServiceStatus.APPROVED.value,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )

    # @patch(
    #     "registry.application.services.service_publisher_service.ServicePublisherService.publish_offchain_service_configs")
    # @patch(
    #     "registry.application.services.service_publisher_service.ServicePublisherService.publish_to_ipfs")
    # @patch(
    #     "registry.application.services.service_publisher_service.ServicePublisherService.get_existing_service_details_from_contract_api")
    # @patch(
    #     "registry.application.services.service_publisher_service.ServicePublisherService.publish_service_data_to_ipfs")
    # @patch("common.ipfs_util.IPFSUtil.read_file_from_ipfs")
    # def test_validate_metadata(self, mock_read_ipfs, mock_publish_to_ipfs,
    #                            mock_existing_service_details_from_contract_api, mock_ipfs_hash,
    #                            mock_publish_offchain_configs):
    #     event = {
    #         "path": "/org/test_org_uuid/service/test_service_uuid/publish",
    #         "requestContext": {
    #             "authorizer": {
    #                 "claims": {
    #                     "email": "karl@dummy.io"
    #                 }
    #             }
    #         },
    #         "httpMethod": "GET",
    #         "pathParameters": {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid"}
    #     }

    #     mock_publish_offchain_configs.return_value = False

    #     # blockchain false
    #     mock_publish_to_ipfs.return_value = ServicePublisherRepository().get_service_for_given_service_uuid(
    #         org_uuid="test_org_uuid", service_uuid="test_service_uuid")
    #     mock_read_ipfs.return_value = {'version': 1,
    #                                    'display_name': 'test_display_name',
    #                                    'encoding': 'proto',
    #                                    'service_type': 'grpc',
    #                                    'model_ipfs_hash': 'QmcdTYvTxEJrv18Ui1vo1wNDisw8BMoFRMQyM13rz1ok5B',
    #                                    'mpe_address': '#12345678', 'groups': [
    #             {'free_calls': 10, 'free_call_signer_address': '0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F',
    #              'daemon_addresses': ['0xq2w3e4rr5t6y7u8i9'],
    #              'pricing': [{'default': True, 'price_model': 'fixed_price', 'price_in_cogs': 1}],
    #              'endpoints': ['https://dummydaemonendpoint.io'], 'group_id': 'test_group_id',
    #              'group_name': 'default_group'}], 'service_description': {'url': 'https://dummy.io',
    #                                                                       'short_description': 'test_short_description',
    #                                                                       'description': 'test_description'},
    #                                    'media': [], 'contributors': [],
    #                                    'tags': []}
    #     mock_existing_service_details_from_contract_api.return_value = {
    #         'ipfs_hash': 'QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf',
    #         "demo_component_required": 0,
    #         "demo_component": {
    #             "demo_component_required": 0,
    #         }
    #     }
    #     response = publish_service(event=event, context=None)
    #     assert response["statusCode"] == 200
    #     assert json.loads(response["body"])["data"] == {'publish_to_blockchain': False}
    #     service = ServicePublisherRepository().get_service_for_given_service_uuid(
    #         org_uuid="test_org_uuid", service_uuid="test_service_uuid")
    #     assert service.service_state.state == ServiceStatus.PUBLISHED.value

    #     # blockchain true
    #     mock_ipfs_hash.return_value = "sample_hash"
    #     mock_read_ipfs.return_value = {'version': 1,
    #                                    'display_name': 'test_display_name',
    #                                    'encoding': 'proto',
    #                                    'service_type': 'grpc',
    #                                    'model_ipfs_hash': 'QmcdTYvTxEJrv18Ui1vo1wNDisw8BMoFRMQyM13rz1ok5B',
    #                                    'mpe_address': '#12345678', 'groups': [
    #             {'free_calls': 10, 'free_call_signer_address': '0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F',
    #              'daemon_addresses': ['0xq2w3e4rr5t6y7u8i9'],
    #              'pricing': [{'default': True, 'price_model': 'fixed_price', 'price_in_cogs': 1}],
    #              'endpoints': ['https://dummydaemonendpoint.io'], 'group_id': 'test_group_id',
    #              'group_name': 'default_group'}], 'service_description': {'url': 'https://dummy.io',
    #                                                                       'short_description': 'test_short_description',
    #                                                                       'description': 'test_description'},
    #                                    'media': [], 'contributors': [],
    #                                    'tags': ["tag1"]}
    #     mock_existing_service_details_from_contract_api.return_value = {
    #         'ipfs_hash': 'QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf',
    #         "demo_component_required": 0
    #     }
    #     response = publish_service(event=event, context=None)
    #     assert response["statusCode"] == 200
    #     assert json.loads(response["body"])["data"] == {'publish_to_blockchain': True,
    #                                                     "service_metadata_ipfs_hash": "ipfs://sample_hash"
    #                                                     }

    #     # blockchain true --> [publish demo component]
    #     mock_ipfs_hash.return_value = "sample_hash"
    #     mock_read_ipfs.return_value = {'version': 1,
    #                                    'display_name': 'test_display_name',
    #                                    'encoding': 'proto',
    #                                    'service_type': 'grpc',
    #                                    'model_ipfs_hash': 'QmcdTYvTxEJrv18Ui1vo1wNDisw8BMoFRMQyM13rz1ok5B',
    #                                    'mpe_address': '#12345678', 'groups': [
    #             {'free_calls': 10, 'free_call_signer_address': '0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F',
    #              'daemon_addresses': ['0xq2w3e4rr5t6y7u8i9'],
    #              'pricing': [{'default': True, 'price_model': 'fixed_price', 'price_in_cogs': 1}],
    #              'endpoints': ['https://dummydaemonendpoint.io'], 'group_id': 'test_group_id',
    #              'group_name': 'default_group'}], 'service_description': {'url': 'https://dummy.io',
    #                                                                       'short_description': 'test_short_description',
    #                                                                       'description': 'test_description'},
    #                                    'media': [], 'contributors': [],
    #                                    'tags': ["tag1"]}
    #     mock_existing_service_details_from_contract_api.return_value = {
    #         'ipfs_hash': 'QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf',
    #         "demo_component_required": 0,
    #         "demo_component": {
    #             "demo_component_required": 1,
    #             "demo_component_last_modified": "2020-08-19T04:10:21"
    #         }
    #     }
    #     response = publish_service(event=event, context=None)
    #     assert response["statusCode"] == 200
    #     assert json.loads(response["body"])["data"] == {'publish_to_blockchain': True,
    #                                                     "service_metadata_ipfs_hash": "ipfs://sample_hash"
    #                                                     }

    #     # Validate meta
    #     org_repo.session.query(ServiceGroupDBModel).delete()
    #     org_repo.session.commit()
    #     mock_publish_to_ipfs.return_value = ServicePublisherRepository().get_service_for_given_service_uuid(
    #         org_uuid="test_org_uuid", service_uuid="test_service_uuid")
    #     mock_ipfs_hash.return_value = "sample_hash"
    #     mock_read_ipfs.return_value = {'version': 1,
    #                                    'display_name': 'test_display_name',
    #                                    'encoding': 'proto',
    #                                    'service_type': 'grpc',
    #                                    'model_ipfs_hash': 'QmcdTYvTxEJrv18Ui1vo1wNDisw8BMoFRMQyM13rz1ok5B',
    #                                    'mpe_address': '#12345678', 'groups': [
    #             {'free_calls': 10, 'free_call_signer_address': '0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F',
    #              'daemon_addresses': ['0xq2w3e4rr5t6y7u8i9'],
    #              'pricing': [{'default': True, 'price_model': 'fixed_price', 'price_in_cogs': 1}],
    #              'endpoints': ['https://dummydaemonendpoint.io'], 'group_id': 'test_group_id',
    #              'group_name': 'default_group'}], 'service_description': {'url': 'https://dummy.io',
    #                                                                       'short_description': 'test_short_description',
    #                                                                       'description': 'test_description'},
    #                                    'media': [], 'contributors': [],
    #                                    'tags': []}
    #     mock_existing_service_details_from_contract_api.return_value = {
    #         'ipfs_hash': 'QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf',
    #         "demo_component_required": 1
    #     }
    #     response = publish_service(event=event, context=None)
    #     assert response["statusCode"] == 500

    def tearDown(self):
        org_repo.session.query(OrganizationStateDBModel).delete()
        org_repo.session.query(OrganizationMemberDBModel).delete()
        org_repo.session.query(OrganizationDBModel).delete()
        org_repo.session.query(ServiceDBModel).delete()
        org_repo.session.query(ServiceGroupDBModel).delete()
        org_repo.session.query(ServiceStateDBModel).delete()
        org_repo.session.query(ServiceReviewHistoryDBModel).delete()
        org_repo.session.query(OffchainServiceConfigDBModel).delete()
        org_repo.session.commit()
