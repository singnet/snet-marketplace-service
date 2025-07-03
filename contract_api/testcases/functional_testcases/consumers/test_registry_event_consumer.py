from unittest import TestCase
from unittest.mock import patch

from contract_api.infrastructure.repositories.organization_repository import OrganizationRepository
from contract_api.infrastructure.repositories.service_repository import ServiceRepository
from contract_api.application.handlers.consumer_handlers import registry_event_consumer


class TestRegistryEventConsumer(TestCase):
    def setUp(self):
        self.service_repository = ServiceRepository()
        self.organization_repository = OrganizationRepository()

    def tearDown(self):
        pass

    @patch('contract_api.application.consumers.organization_event_consumers.OrganizationCreatedEventConsumer._get_org_details_from_blockchain')
    @patch('contract_api.application.consumers.event_consumer.EventConsumer._push_asset_to_s3_using_hash')
    def test_a_organization_created(self, push_assets_to_s3, get_org_details_from_blockchain):
        event = event = {'Records': [
            {'body': '{\n "Message" : "{\\"blockchain_name\\": \\"Ethereum\\", \\"blockchain_event\\": {\\"name\\": \\"OrganizationCreated\\", \\"data\\": {\\"block_no\\": 8640583, \\"from_address\\": \\"0xeDFb9c1e6C4ac9A2333552C5F52a0acaeB555EA8\\", \\"to_address\\": \\"0xE73aC4AC2D9Df5698710fFB2f6c3923ADf0bA055\\", \\"json_str\\": \\"{\'orgId\': b\'190625\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\'}\\", \\"transaction_hash\\": \\"0x38fd6accd2103bd041571b6081acaf845083d4b2878599a91217f76694b6e5cb\\", \\"log_index\\": 8}}}"\n}'}
        ]}

        mock_org_metadata = {
            "org_name": "190625",
            "org_id": "190625",
            "org_type": "organization",
            "description": {
                "description": "123",
                "short_description": "123",
                "url": "https://abcde.ee"
            },
            "assets": {
                "hero_image": "ipfs://QmNke5txcsWo6wgS1VtNgwtTZ2c8S6A8kNapjkerH3JGyc"
            },
            "contacts": [
                {
                    "email": "",
                    "phone": "+3725658060",
                    "contact_type": "general"
                },
                {
                    "email": "abc@de.ee",
                    "phone": "+3725658060",
                    "contact_type": "support"
                }
            ],
            "groups": [
                {
                    "group_name": "default_group",
                    "group_id": "1/W0xmq+sDfjXLS2AIGAd79hOKFgpPlw5MC5kX5AIdo=",
                    "payment": {
                        "payment_address": "0xeDFb9c1e6C4ac9A2333552C5F52a0acaeB555EA8",
                        "payment_expiration_threshold": 40320,
                        "payment_channel_storage_type": "etcd",
                        "payment_channel_storage_client": {
                            "connection_timeout": "5s",
                            "request_timeout": "3s",
                            "endpoints": [
                                "http://127.0.0.1:2379"
                            ]
                        }
                    }
                }
            ]
        }
        blockchain_data = ("190625", ["190625", "", "", "0xeDFb9c1e6C4ac9A2333552C5F52a0acaeB555EA8"], mock_org_metadata, "abc")
        mock_s3_url = "http://test-s3-push"

        get_org_details_from_blockchain.return_value = blockchain_data
        push_assets_to_s3.return_value = mock_s3_url

        registry_event_consumer(event, context = None)

        org = self.organization_repository.get_organization(org_id = "190625")

        assert org is not None
        assert org.org_id == "190625"
        assert org.organization_name == "190625"
        assert org.description == {"description": "123", "short_description": "123", "url": "https://abcde.ee"}
        assert org.contacts == [{"email": "", "phone": "+3725658060", "contact_type": "general"}, {"email": "abc@de.ee", "phone": "+3725658060", "contact_type": "support"}]

        groups = self.organization_repository.get_groups(org_id = "190625")

        assert len(groups) == 1
        group = groups[0]
        assert group.group_name == "default_group"
        assert group.group_id == "1/W0xmq+sDfjXLS2AIGAd79hOKFgpPlw5MC5kX5AIdo="
        assert group.payment == {
                        "payment_address": "0xeDFb9c1e6C4ac9A2333552C5F52a0acaeB555EA8",
                        "payment_expiration_threshold": 40320,
                        "payment_channel_storage_type": "etcd",
                        "payment_channel_storage_client": {
                            "connection_timeout": "5s",
                            "request_timeout": "3s",
                            "endpoints": [
                                "http://127.0.0.1:2379"
                            ]
                        }
                    }


    @patch('contract_api.infrastructure.storage_provider.StorageProvider.get')
    @patch('common.blockchain_util.BlockChainUtil.read_contract_address')
    @patch('contract_api.application.consumers.event_consumer.EventConsumer._push_asset_to_s3_using_hash')
    @patch('contract_api.application.consumers.service_event_consumers.ServiceCreatedDeploymentEventHandler.process_service_deployment')
    def test_b_service_created(self, process_service_deployment, push_assets_to_s3, read_contract_address, storage_provider_get):
        event = {'Records': [
            {'body': '{\n "Message" : "{\\"blockchain_name\\": \\"Ethereum\\", \\"blockchain_event\\": {\\"name\\": \\"ServiceCreated\\", \\"data\\": {\\"block_no\\": 8640583, \\"from_address\\": \\"0xeDFb9c1e6C4ac9A2333552C5F52a0acaeB555EA8\\", \\"to_address\\": \\"0xE73aC4AC2D9Df5698710fFB2f6c3923ADf0bA055\\", \\"json_str\\": \\"{\'orgId\': b\'190625\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\', \'serviceId\': b\'190625_2\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\', \'metadataURI\': b\'ipfs://QmYVYBxjCxLWYYnz6bK5kHYVW8JBfFLwn4MGzEpMiF7LZ1\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\'}\\", \\"transaction_hash\\": \\"0x38fd6accd2103bd041571b6081acaf845083d4b2878599a91217f76694b6e5cb\\", \\"log_index\\": 8}}}"\n}'}
        ]}

        mock_service_metadata = {
            "version": 1,
            "display_name": "190625_2",
            "encoding": "proto",
            "service_type": "grpc",
            "service_api_source": "ipfs://QmSba2aTtPF8oDP8CzBPfhPvahj4a9gcASK6U68pLm3GEy",
            "mpe_address": "0x03e7D37A13ed807B2311418095E23fA8Ff9DE192",
            "groups": [
                {
                    "free_calls": 1,
                    "free_call_signer_address": "0xeDFb9c1e6C4ac9A2333552C5F52a0acaeB555EA8",
                    "daemon_addresses": [
                        "0x3626171F2205AEffE914d3e6cf55495CaBDfc998"
                    ],
                    "pricing": [
                        {
                            "default": True,
                            "price_model": "fixed_price",
                            "price_in_cogs": 1
                        }
                    ],
                    "endpoints": [
                        "https://tosssky.hopto.org:5279"
                    ],
                    "group_id": "1/W0xmq+sDfjXLS2AIGAd79hOKFgpPlw5MC5kX5AIdo=",
                    "group_name": "default_group"
                }
            ],
            "service_description": {
                "url": "https://totsky.ee/",
                "short_description": "123",
                "description": "123"
            },
            "media": [
                {
                    "order": 1,
                    "url": "https://dev-fet-marketplace-service-assets.s3.us-east-1.amazonaws.com/a32d4af601344d27a631e5d2a3f612cb/services/a7000a8e9a09496c826086fd14a09ca2/assets/20250619074449_asset.png",
                    "file_type": "image",
                    "asset_type": "hero_image",
                    "alt_text": ""
                }
            ],
            "contributors": [
                {
                    "name": "Vjatseslav",
                    "email_id": ""
                }
            ],
            "tags": [
                "123"
            ]
        }
        mock_mpe_address = "0x03e7D37A13ed807B2311418095E23fA8Ff9DE192"
        mock_s3_url = "http://test-s3-push"
        mock_deployment_none = None

        storage_provider_get.return_value = mock_service_metadata
        read_contract_address.return_value = mock_mpe_address
        push_assets_to_s3.return_value = mock_s3_url
        process_service_deployment.return_value = mock_deployment_none

        registry_event_consumer(event, context = None)

        result = self.service_repository.get_service(org_id = "190625", service_id = "190625_2")

        assert result is not None

        service, organization, service_metadata = result
        assert service.service_id == "190625_2"
        assert service.org_id == "190625"
        assert service.is_curated
        assert service_metadata.service_id == "190625_2"
        assert service_metadata.org_id == "190625"
        assert service_metadata.mpe_address == "0x03e7D37A13ed807B2311418095E23fA8Ff9DE192"


    def test_c_service_deleted(self):
        event = {'Records': [
            {
                'body': '{\n "Message" : "{\\"blockchain_name\\": \\"Ethereum\\", \\"blockchain_event\\": {\\"name\\": \\"ServiceDeleted\\", \\"data\\": {\\"block_no\\": 8640583, \\"from_address\\": \\"0xeDFb9c1e6C4ac9A2333552C5F52a0acaeB555EA8\\", \\"to_address\\": \\"0xE73aC4AC2D9Df5698710fFB2f6c3923ADf0bA055\\", \\"json_str\\": \\"{\'orgId\': b\'190625\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\', \'serviceId\': b\'190625_2\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\'}\\", \\"transaction_hash\\": \\"0x38fd6accd2103bd041571b6081acaf845083d4b2878599a91217f76694b6e5cb\\", \\"log_index\\": 8}}}"\n}'}
        ]}

        registry_event_consumer(event, context = None)

        result = self.service_repository.get_service(org_id = "190625", service_id = "190625_2")

        assert result is None

    def test_d_organization_deleted(self):
        event = {'Records': [
            {
                'body': '{\n "Message" : "{\\"blockchain_name\\": \\"Ethereum\\", \\"blockchain_event\\": {\\"name\\": \\"OrganizationDeleted\\", \\"data\\": {\\"block_no\\": 8640583, \\"from_address\\": \\"0xeDFb9c1e6C4ac9A2333552C5F52a0acaeB555EA8\\", \\"to_address\\": \\"0xE73aC4AC2D9Df5698710fFB2f6c3923ADf0bA055\\", \\"json_str\\": \\"{\'orgId\': b\'190625\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\\\\\\\\x00\'}\\", \\"transaction_hash\\": \\"0x38fd6accd2103bd041571b6081acaf845083d4b2878599a91217f76694b6e5cb\\", \\"log_index\\": 8}}}"\n}'}
        ]}

        registry_event_consumer(event, context = None)

        result = self.organization_repository.get_organization(org_id = "190625")

        assert result is None
