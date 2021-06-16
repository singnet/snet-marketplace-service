import json
from datetime import datetime as dt
from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

from common.constant import StatusCode
from registry.application.handlers.service_handlers import create_service
from registry.application.handlers.service_handlers import get_daemon_config_for_current_network
from registry.application.handlers.service_handlers import get_service_for_service_uuid
from registry.application.handlers.service_handlers import get_services_for_organization
from registry.application.handlers.service_handlers import legal_approval_of_service
from registry.application.handlers.service_handlers import list_of_orgs_with_services_submitted_for_approval
from registry.application.handlers.service_handlers import publish_service_metadata_to_ipfs
from registry.application.handlers.service_handlers import save_service
from registry.application.handlers.service_handlers import save_service_attributes, verify_service_id
from registry.application.handlers.service_handlers import save_transaction_hash_for_published_service
from registry.application.handlers.service_handlers import submit_service_for_approval
from registry.constants import EnvironmentType
from registry.constants import OrganizationMemberStatus
from registry.constants import Role
from registry.constants import ServiceAvailabilityStatus
from registry.constants import ServiceStatus
from registry.domain.factory.service_factory import ServiceFactory
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


class TestService(TestCase):
    def setUp(self):
        pass

    def test_verify_service_id(self):
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
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )
        new_org_members = [
            {
                "username": "karl@dummy.io",
                "address": "0x123"
            },
            {
                "username": "trax@dummy.io",
                "address": "0x234"
            },
            {
                "username": "dummy_user1@dummy.io",
                "address": "0x345"
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
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid",
                display_name="test_display_name",
                service_id="test_service_id",
                metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
                proto={},
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                assets={},
                rating={},
                ranking=1,
                contributors=[],
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "GET",
            "pathParameters": {"org_uuid": "test_org_uuid"},
            "queryStringParameters": {"service_id": "test_service_id"}
        }
        response = verify_service_id(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"] == ServiceAvailabilityStatus.UNAVAILABLE.value)
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "GET",
            "pathParameters": {"org_uuid": "test_org_uuid"},
            "queryStringParameters": {"service_id": "new_test_service_id"}
        }
        response = verify_service_id(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"] == ServiceAvailabilityStatus.AVAILABLE.value)

    def test_create_service(self):
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
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )

        new_org_members = [
            {
                "username": "dummy_user1@dummy.io",
                "address": "0x345"
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

        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "POST",
            "pathParameters": {"org_uuid": "test_org_uuid"},
            "body": json.dumps({"display_name": "test_display_name"})
        }
        response = create_service(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["org_uuid"] == "test_org_uuid")

    def test_get_services_for_organization(self):
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
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )
        new_org_members = [
            {
                "username": "karl@dummy.io",
                "address": "0x123"
            },
            {
                "username": "trax@dummy.io",
                "address": "0x234"
            },
            {
                "username": "dummy_user1@dummy.io",
                "address": "0x345"
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
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid",
                display_name="test_display_name",
                service_id="test_service_id",
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
                service_uuid="test_service_uuid",
                state="DRAFT",
                transaction_hash=None,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceGroupDBModel(
                row_id="1000",
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid",
                group_id="test_group_id",
                pricing={},
                endpoints={"https://dummydaemonendpoint.io": {"verfied": True}},
                daemon_address=["0xq2w3e4rr5t6y7u8i9"],
                free_calls=10,
                free_call_signer_address="",
                created_on=dt.utcnow()
            )
        )
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "GET",
            "pathParameters": {"org_uuid": "test_org_uuid"},
            "body": json.dumps({
                "q": "display",
                "limit": 10,
                "offset": 0,
                "s": "all",
                "sort_by": "display_name",
                "order_by": "desc",
                "filters": []
            })
        }
        response = get_services_for_organization(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["total_count"] == 1)
        assert (response_body["data"]["offset"] == 0)
        assert (response_body["data"]["limit"] == 10)
        assert (len(response_body["data"]["result"]) == 1)

    def test_save_service(self):
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
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )
        new_org_members = [
            {
                "username": "karl@dummy.io",
                "address": "0x123"
            },
            {
                "username": "trax@dummy.io",
                "address": "0x234"
            },
            {
                "username": "dummy_user1@dummy.io",
                "address": "0x345"
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
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid",
                display_name="test_display_name",
                service_id="test_service_id",
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
                service_uuid="test_service_uuid",
                state=ServiceStatus.DRAFT.value,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceGroupDBModel(
                row_id="1000",
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid",
                group_id="test_group_id",
                endpoints={"https://dummydaemonendpoint.io": {"verfied": True}},
                daemon_address=["0xq2w3e4rr5t6y7u8i9"],
                free_calls=10,
                free_call_signer_address="0xq2s3e4r5t6y7u8i9o0",
                created_on=dt.utcnow()
            )
        )
        event = {
            "path": "/org/test_org_uuid/service",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "PUT",
            "pathParameters": {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid"},
            "body": json.dumps({
                "description": "test description updated 1",
                "groups": [
                    {
                        "group_name": "defaultGroup",
                        "group_id": "l/hp6f1RXFPANeLWFZYwTB93Xi42S8NpZHfnceS6eUw=",
                        "free_calls": 10,
                        "free_call_signer_address": "0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F",
                        "pricing": [
                            {
                                "default": True,
                                "price_model": "fixed_price",
                                "price_in_cogs": 1
                            }
                        ],
                        "endpoints": {}
                    }
                ]
            })
        }
        response = save_service(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["service_uuid"] == "test_service_uuid")
        assert (response_body["data"]["service_state"]["state"] == ServiceStatus.DRAFT.value)
        event = {
            "path": "/org/test_org_uuid/service",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "PUT",
            "pathParameters": {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid"},
            "body": json.dumps({
                "description": "test description updated 2",
                "groups": [
                    {
                        "group_name": "defaultGroup",
                        "group_id": "l/hp6f1RXFPANeLWFZYwTB93Xi42S8NpZHfnceS6eUw=",
                        "free_calls": 20,
                        "free_call_signer_address": "0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F",
                        "pricing": [
                            {
                                "default": True,
                                "price_model": "fixed_price",
                                "price_in_cogs": 2
                            }
                        ],
                        "endpoints": {}
                    }
                ]
            })
        }
        response = save_service(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["service_uuid"] == "test_service_uuid")
        assert (response_body["data"]["service_state"]["state"] == ServiceStatus.DRAFT.value)

    def test_get_service_for_service_uuid(self):
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
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )
        new_org_members = [
            {
                "username": "karl@dummy.io",
                "address": "0x123"
            },
            {
                "username": "trax@dummy.io",
                "address": "0x234"
            },
            {
                "username": "dummy_user1@dummy.io",
                "address": "0x345"
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
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid",
                display_name="test_display_name",
                service_id="test_service_id",
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
                service_uuid="test_service_uuid",
                state=ServiceStatus.DRAFT.value,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )

        event = {
            "path": "/org/test_org_uuid/service",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "GET",
            "pathParameters": {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid"}
        }
        response = get_service_for_service_uuid(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["org_uuid"] == "test_org_uuid")
        assert (response_body["data"]["service_uuid"] == "test_service_uuid")
        assert (response_body["data"]["service_state"]["state"] == ServiceStatus.DRAFT.value)

    @patch("registry.application.services.service_publisher_service.ServicePublisherService.publish_to_ipfs")
    def test_get_service_metadata_uri(self, mock_ipfs):
        mock_ipfs.return_value = "QmeoVWV99BJoa9czuxg6AiSyFiyVNNFpcaSMYTQUft785u"

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
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )
        new_org_members = [
            {
                "username": "karl@dummy.io",
                "address": "0x123"
            },
            {
                "username": "trax@dummy.io",
                "address": "0x234"
            },
            {
                "username": "dummy_user1@dummy.io",
                "address": "0x345"
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
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid",
                display_name="test_display_name",
                service_id="test_service_id",
                metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
                short_description="test_short_description",
                description="test_long_description",
                project_url="https://test_project_url.com",
                proto={"encoding": "proto", "service_type": "grpc", "model_ipfs_hash": "test_model_ipfs_hash"},
                ranking=1,
                assets={"proto_files": {
                    "url": "https://ropsten-marketplace-service-assets.s3.amazonaws.com/test_org_uuid/services/test_service_uuid/assets/20200212111248_proto_files.zip"},
                    "hero_image": {
                        "url": "https://ropsten-marketplace-service-assets.s3.amazonaws.com/ba88d221c5264d6f859e62b15ddd63cf/services/b36f882be79043e18ae0f7c946128b31/assets/20200310063017_asset.png",
                        "ipfs_hash": ""}, "demo_files": {
                        "url": "https://ropsten-marketplace-service-assets.s3.amazonaws.com/ba88d221c5264d6f859e62b15ddd63cf/services/b36f882be79043e18ae0f7c946128b31/component/20200310063120_component.zip"}},
                created_on=dt.utcnow()
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
        event = {
            "path": "/org/test_org_uuid/service/test_service_uuid/ipfs_publish",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "POST",
            "pathParameters": {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid"}
        }
        response = publish_service_metadata_to_ipfs(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def test_save_transaction_hash_for_published_service(self):
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
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )
        new_org_members = [
            {
                "username": "karl@dummy.io",
                "address": "0x123"
            },
            {
                "username": "trax@dummy.io",
                "address": "0x234"
            },
            {
                "username": "dummy_user1@dummy.io",
                "address": "0x345"
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
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid",
                display_name="test_display_name",
                service_id="test_service_id",
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
                service_uuid="test_service_uuid",
                state=ServiceStatus.APPROVED.value,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )
        event = {
            "path": "/org/test_org_uuid/service/test_service_uuid/transaction",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "POST",
            "pathParameters": {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid"},
            "body": json.dumps({"transaction_hash": "0xtest_trxn_hash"})
        }
        response = save_transaction_hash_for_published_service(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"] == StatusCode.OK)

    def test_list_of_orgs_with_services_submitted_for_approval(self):
        service_repo.add_item(
            ServiceReviewHistoryDBModel(
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid",
                service_metadata={},
                state=ServiceStatus.APPROVAL_PENDING.value,
                reviewed_by=None,
                reviewed_on=None,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()

            )
        )
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
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )
        new_org_members = [
            {
                "username": "dummy_user1@dummy.io",
                "address": "0x345"
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
        event = {
            "path": "/admin/orgs/services",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "GET"
        }
        response = list_of_orgs_with_services_submitted_for_approval(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"][0]["org_uuid"] == "test_org_uuid")
        assert (response_body["data"][0]["services"][0]["service_uuid"] == "test_service_uuid")

    def test_legal_approval_of_service(self):
        service_repo.add_item(
            ServiceReviewHistoryDBModel(
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid",
                service_metadata={},
                state=ServiceStatus.APPROVAL_PENDING.value,
                reviewed_by=None,
                reviewed_on=None,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()

            )
        )
        event = {
            "path": "/admin/org/test_org_uuid/service/test_service_uuid",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "POST",
            "pathParameters": {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid"},
        }
        response = legal_approval_of_service(event, context=None)

    @patch(
        "registry.domain.services.registry_blockchain_util.RegistryBlockChainUtil.register_or_update_service_in_blockchain")
    @patch("common.utils.publish_zip_file_in_ipfs")
    @patch("common.ipfs_util.IPFSUtil.write_file_in_ipfs")
    @patch("common.utils.send_email_notification")
    @patch("common.utils.Utils.report_slack")
    def test_submit_service_for_approval(self, report_slack, email_notification, file_ipfs_hash,
                                         zip_file_ipfs_hash, blockchain_transaction):
        blockchain_transaction.return_value = "0x2w3e4r5t6y7u8i9o0oi8u7y6t5r4e3w2"
        zip_file_ipfs_hash.return_value = "Qwertyuiopasdfghjklzxcvbnm"
        file_ipfs_hash.return_value = "Qzertyuiopasdfghjklzxcvbnn"
        self.tearDown()
        test_org_uuid = "test_org_uuid"
        test_service_uuid = "test_service_uuid"
        test_user = "dummy@dummy.io"
        org_repo.add_item(
            OrganizationDBModel(
                name="test_org",
                org_id="test_org_id",
                uuid=test_org_uuid,
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
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )
        org_repo.add_item(
            OrganizationStateDBModel(
                org_uuid=test_org_uuid,
                state="PUBLISHED",
                created_by=test_user,
                updated_by=test_user
            )
        )
        new_org_members = [
            {
                "username": test_user,
                "address": "0x345"
            }

        ]
        org_repo.add_all_items(
            [
                OrganizationMemberDBModel(
                    username=member["username"],
                    org_uuid=test_org_uuid,
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
        service_repo.add_item(
            ServiceDBModel(
                org_uuid=test_org_uuid,
                uuid=test_service_uuid,
                display_name="test_display_name",
                service_id="test_service_id",
                metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                ranking=1,
                proto={"proto_files": {
                    "url": "https://ropsten-marketplace-service-assets.s3.amazonaws.com/test_org_uuid/services/test_service_uuid/assets/20200212111248_proto_files.zip"}},
                contributors=[{"email_id": "dev@dummy.io", "name": "contributor"}],
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceStateDBModel(
                row_id=1000,
                org_uuid=test_org_uuid,
                service_uuid=test_service_uuid,
                state=ServiceStatus.DRAFT.value,
                created_by=test_user,
                updated_by=test_user,
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceGroupDBModel(
                row_id="1000",
                org_uuid=test_org_uuid,
                service_uuid=test_service_uuid,
                group_id="test_group_id",
                endpoints=["https://dummydaemonendpoint.io"],
                daemon_address=["0xq2w3e4rr5t6y7u8i9"],
                free_calls=10,
                free_call_signer_address="0xq2s3e4r5t6y7u8i9o0",
                created_on=dt.utcnow()
            )
        )
        event = {
            "path": "/org/test_org_uuid/service",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": test_user
                    }
                }
            },
            "httpMethod": "PUT",
            "pathParameters": {"org_uuid": test_org_uuid, "service_uuid": test_service_uuid},
            "body": json.dumps({
                "org_id": "curation",
                "service_id": "test_service_id",
                "display_name": "test_display_name",
                "description": "test description updated",
                "mpe_address": "0xq2w3e4r5t6y7u8i9i98u7y6t5r4e3w2",
                "assets": {
                    "proto_files": {
                        "url": "https://ropsten-marketplace-service-assets.s3.amazonaws.com/test_org_uuid/services/test"
                               "_service_uuid/assets/20200212111248_proto_files.zip"
                    }
                },
                "contributors": [{"name": "dummy", "email_id": "dev@dummy.io"}],
                "groups": [{"group_name": "default_group",
                            "free_calls": 12,
                            "free_call_signer_address": "0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F",
                            "daemon_address": ["0x1234", "0x345"],
                            "pricing": [
                                {
                                    "price_model": "fixed_price",
                                    "price_in_cogs": 1,
                                    "default": True
                                }
                            ],
                            "endpoints": {
                                "https://tz-services-1.snet.sh:8005": {}
                            },
                            "test_endpoints": [
                                "https://tz-services-1.snet.sh:8005"
                            ],
                            "group_id": "EoFmN3nvaXpf6ew8jJbIPVghE5NXfYupFF7PkRmVyGQ="

                            }]
            }
            )
        }
        response = submit_service_for_approval(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["service_uuid"] == test_service_uuid)
        assert (response_body["data"]["service_state"]["state"] == ServiceStatus.APPROVAL_PENDING.value)
        self.assertListEqual(
            [{"name": "dummy", "email_id": "dev@dummy.io"}, {"name": "", "email_id": test_user}],
            response_body["data"]["contributors"])

    def test_daemon_config_for_test_and_main_environment(self):
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
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )
        new_org_members = [

            {
                "username": "dummy_user1@dummy.io",
                "address": "0x345"
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
                state="PUBLISHED",
                created_by="dummy_user1@dummy.io",
                updated_by="dummy_user1@dummy.io"
            )
        )

        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid",
                display_name="test_display_name",
                service_id="test_service_id",
                metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                ranking=1,
                proto={"proto_files": {
                    "url": "https://ropsten-marketplace-service-assets.s3.amazonaws.com/test_org_uuid/services/test_service_uuid/assets/20200212111248_proto_files.zip"}},
                contributors={"email_id": "prashant@singularitynet.io"},
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceStateDBModel(
                row_id=1000,
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid",
                state=ServiceStatus.DRAFT.value,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )
        event = {"path": "/org/test_org_uuid/service/test_service_uuid/group_id/test_group_id/daemon/config",
                 "requestContext": {
                     "authorizer": {
                         "claims": {
                             "email": "dummy_user1@dummy.io"
                         }
                     }
                 }, "httpMethod": "GET",
                 "pathParameters": {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid",
                                    "group_id": "test_group_id"},
                 "queryStringParameters": {"network": EnvironmentType.MAIN.value}}
        response = get_daemon_config_for_current_network(event, "")
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["blockchain_enabled"] is True)
        assert (response_body["data"]["passthrough_enabled"] is True)

    def test_service_to_metadata(self):
        payload = {"service_id": "sdfadsfd1", "display_name": "new_service_123",
                             "short_description": "sadfasd", "description": "dsada", "project_url": "df",
                             "proto": {},
                             "assets": {"proto_files": {
                                 "url": "https://ropsten-marketplace-service-assets.s3.amazonaws.com/9887ec2e099e4afd92c4a052737eaa97/services/7420bf47989e4afdb1797d1bba8090aa/proto/20200327130256_proto_files.zip",
                                 "ipfs_hash": "QmUfDprFisFeaRnmLEqks1AFN6iam5MmTh49KcomXHEiQY"}, "hero_image": {
                                 "url": "https://ropsten-marketplace-service-assets.s3.amazonaws.com/9887ec2e099e4afd92c4a052737eaa97/services/7420bf47989e4afdb1797d1bba8090aa/assets/20200323130126_asset.png",
                                 "ipfs_hash": ""}, "demo_files": {
                                 "url": "https://ropsten-marketplace-service-assets.s3.amazonaws.com/9887ec2e099e4afd92c4a052737eaa97/services/7420bf47989e4afdb1797d1bba8090aa/component/20200401121414_component.zip",
                                 "ipfs_hash": "QmUfDprFisFeaRnmLEqks1AFN6iam5MmTh49KcomXHEiQY"}},
                             "contributors": [{"name": "df", "email_id": ""}], "groups": [
                {"group_name": "default_group", "group_id": "a+8V4tUs+DBnZfxoh2vBHVv1pAt8pkCac8mpuKFltTo=",
                 "free_calls": 23, "free_call_signer_address": "0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F",
                 "pricing": [{"default": True, "price_model": "fixed_price", "price_in_cogs": 1}],
                 "endpoints": {"https://example-service-a.singularitynet.io:8085": {"valid": False}},
                 "test_endpoints": ["https://example-service-a.singularitynet.io:8085"],
                 "daemon_addresses": ["https://example-service-a.singularitynet.io:8085"]}], "tags": ["adsf"],
                             "comments": {"SERVICE_PROVIDER": "", "SERVICE_APPROVER": "<div></div>"},
                             "mpe_address": "0x8fb1dc8df86b388c7e00689d1ecb533a160b4d0c"}

        service = ServiceFactory.create_service_entity_model("", "", payload, ServiceStatus.APPROVED.value)
        service_metadata = service.to_metadata()
        assert service_metadata == {
            "version": 1,
            "display_name": "new_service_123",
            "encoding": "",
            "service_type": "",
            "model_ipfs_hash": "",
            "mpe_address": "0x8fb1dc8df86b388c7e00689d1ecb533a160b4d0c",
            "groups": [
                {
                    "free_calls": 23,
                    "free_call_signer_address": "0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F",
                    "daemon_addresses": ["https://example-service-a.singularitynet.io:8085"],
                    "pricing": [
                        {"default": True, "price_model": "fixed_price", "price_in_cogs": 1}
                    ],
                    "endpoints": ["https://example-service-a.singularitynet.io:8085"],
                    "group_id": "a+8V4tUs+DBnZfxoh2vBHVv1pAt8pkCac8mpuKFltTo=",
                    "group_name": "default_group"
                }
            ],
            "service_description": {
                "url": "df",
                "short_description": "sadfasd",
                "description": "dsada"
            },
            "media": [
                {
                 "order": 1,
                 "url": "https://ropsten-marketplace-service-assets.s3.amazonaws.com/9887ec2e099e4afd92c4a052737eaa97/services/7420bf47989e4afdb1797d1bba8090aa/assets/20200323130126_asset.png",
                 "file_type": "image",
                 "asset_type": "hero_image",
                 "alt_text": ""
                 }
            ],
            'tags': ['adsf'],
            "contributors": [{"name": "df", "email_id": ""}]
        }

    def test_save_service_attributes(self):
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
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )
        new_org_members = [
            {
                "username": "karl@dummy.io",
                "address": "0x123"
            },
            {
                "username": "trax@dummy.io",
                "address": "0x234"
            },
            {
                "username": "dummy_user1@dummy.io",
                "address": "0x345"
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
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid",
                display_name="test_display_name",
                service_id="test_service_id",
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
                service_uuid="test_service_uuid",
                state=ServiceStatus.APPROVAL_PENDING.value,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceGroupDBModel(
                row_id="1000",
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid",
                group_id="test_group_id",
                endpoints={"https://dummydaemonendpoint.io": {"verfied": True}},
                daemon_address=["0xq2w3e4rr5t6y7u8i9"],
                free_calls=10,
                free_call_signer_address="0xq2s3e4r5t6y7u8i9o0",
                created_on=dt.utcnow()
            )
        )
        event = {
            "path": "/org/test_org_uuid/service",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "PUT",
            "pathParameters": {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid"},
            "body": json.dumps({
                "groups": [
                    {
                        "group_name": "defaultGroup",
                        "group_id": "l/hp6f1RXFPANeLWFZYwTB93Xi42S8NpZHfnceS6eUw=",
                        "free_calls": 15,
                        "free_call_signer_address": "0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F",
                        "pricing": [
                            {
                                "default": True,
                                "price_model": "fixed_price",
                                "price_in_cogs": 1
                            }
                        ],
                "endpoints": {
                                "https://example-service-a.singularitynet.io:8010": {
                                  "valid": False
                                },
                                "https://example-service-a.singularitynet.io:8013": {
                                  "valid": False
                                },
                                "https://example-service-a.singularitynet.io:8011": {
                                  "valid": True
                                }
      },
                    }
                ]
            })
        }
        response = save_service_attributes(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["service_uuid"] == "test_service_uuid")
        assert (response_body["data"]["service_state"]["state"] == ServiceStatus.APPROVAL_PENDING.value)
        assert (response_body["data"]['groups'] == [{'group_id': 'l/hp6f1RXFPANeLWFZYwTB93Xi42S8NpZHfnceS6eUw=', 'group_name': 'defaultGroup', 'endpoints': {'https://example-service-a.singularitynet.io:8010': {'valid': False}, 'https://example-service-a.singularitynet.io:8013': {'valid': False}, 'https://example-service-a.singularitynet.io:8011': {'valid': True}}, 'test_endpoints': [], 'pricing': [{'default': True, 'price_model': 'fixed_price', 'price_in_cogs': 1}], 'free_calls': 15, 'free_call_signer_address': '0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F', 'daemon_addresses': []}])

    def tearDown(self):
        org_repo.session.query(OrganizationStateDBModel).delete()
        org_repo.session.query(OrganizationMemberDBModel).delete()
        org_repo.session.query(OrganizationDBModel).delete()
        org_repo.session.query(ServiceDBModel).delete()
        org_repo.session.query(ServiceGroupDBModel).delete()
        org_repo.session.query(ServiceStateDBModel).delete()
        org_repo.session.query(ServiceReviewHistoryDBModel).delete()
        org_repo.session.commit()
