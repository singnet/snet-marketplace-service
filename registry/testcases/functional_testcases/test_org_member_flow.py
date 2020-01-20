import unittest
from _datetime import datetime as dt
import json
from unittest import TestCase
from unittest.mock import patch
from registry.application.handlers.organization_handlers import get_all_members, invite_members, get_member, \
    verify_code, publish_members, delete_members, register_member, get_all_org
from registry.infrastructure.repositories.organization_repository import OrganizationRepository
from registry.infrastructure.models.models import Organization, OrganizationAddress, OrganizationMember, \
    OrganizationReviewWorkflow
from registry.constants import OrganizationStatus, OrganizationMemberStatus
from common.boto_utils import BotoUtils

org_repo = OrganizationRepository()


class TestOrgMemberFlow(TestCase):

    def test_get_members(self):
        self.tearDown()
        org_repo.add_item(
            Organization(
                row_id=1000,
                name="test_org",
                org_id="test_org_id",
                org_uuid="test_org_uuid",
                type="organization",
                owner="dummyuser@dummy.io",
                owner_name="Test Owner",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                address=[],
                metadata_ipfs_hash="#dummyhashdummyhash"
            )
        )
        org_repo.add_item(
            OrganizationReviewWorkflow(
                org_row_id=1000,
                status=OrganizationStatus.APPROVAL_PENDING.value,
                transaction_hash="",
                wallet_address="",
                created_by="",
                updated_by="",
                approved_by="",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            ))
        org_repo.add_item(
            OrganizationMember(
                org_uuid="test_org_uuid",
                role="MEMBER",
                username="dummy_user1@dummy.io",
                address=None,
                status=OrganizationMemberStatus.PENDING.value,
                transaction_hash="",
                invite_code="asdfghjkl",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummyuser@dummy.io"
                    }
                }
            },
            "httpMethod": "GET",
            "pathParameters": {"org_id": "test_org_uuid"},
            "queryStringParameters": {"status": OrganizationMemberStatus.PENDING.value}

        }
        response = get_all_members(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"][0]["username"] == "dummy_user1@dummy.io")
        assert (response_body["data"][0]["status"] == OrganizationMemberStatus.PENDING.value)
        assert (response_body["data"][0]["role"] == "MEMBER")

    def test_get_member_status(self):
        self.tearDown()
        org_repo.add_item(
            Organization(
                row_id=1000,
                name="test_org",
                org_id="test_org_id",
                org_uuid="test_org_uuid",
                type="organization",
                owner="dummyuser@dummy.io",
                owner_name="Test Owner",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                address=[],
                metadata_ipfs_hash="#dummyhashdummyhash"
            )
        )
        org_repo.add_item(
            OrganizationReviewWorkflow(
                org_row_id=1000,
                status=OrganizationStatus.APPROVAL_PENDING.value,
                transaction_hash="",
                wallet_address="",
                created_by="",
                updated_by="",
                approved_by="",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            ))
        org_repo.add_item(
            OrganizationMember(
                org_uuid="test_org_uuid",
                role="MEMBER",
                username="dummy_user2@dummy.io",
                address="0x123456789",
                status=OrganizationMemberStatus.ACCEPTED.value,
                transaction_hash="",
                invite_code="lkjhgfdsa",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummyuser@dummy.io"
                    }
                }
            }, "httpMethod": "GET", "pathParameters": {"org_id": "test_org_uuid", "username": "dummy_user2@dummy.io"}}
        response = get_member(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"][0]["username"] == "dummy_user2@dummy.io")
        assert (response_body["data"][0]["role"] == "MEMBER")
        assert (response_body["data"][0]["status"] == OrganizationMemberStatus.ACCEPTED.value)

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_invite_members(self, mock_send_notification):
        mock_send_notification.return_value = None
        self.tearDown()
        org_repo.add_item(
            Organization(
                row_id=1000,
                name="test_org",
                org_id="test_org_id",
                org_uuid="test_org_uuid",
                type="organization",
                owner="dummyuser@dummy.io",
                owner_name="Test Owner",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                address=[],
                metadata_ipfs_hash="#dummyhashdummyhash"
            )
        )
        org_repo.add_item(
            OrganizationReviewWorkflow(
                org_row_id=1000,
                status=OrganizationStatus.APPROVAL_PENDING.value,
                transaction_hash="",
                wallet_address="",
                created_by="",
                updated_by="",
                approved_by="",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            ))
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummyuser@dummy.io"
                    }
                }
            },
            "httpMethod": "POST",
            "pathParameters": {"org_id": "test_org_uuid"},
            "body": json.dumps({"members": [{"username": "dummy_user3@dummy.io"},
                                            {"username": "dummy_user4@dummy.io"}]})
        }
        response = invite_members(event=event, context=None)
        assert (response["statusCode"] == 201)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def test_verify_invite_code(self):
        self.tearDown()
        org_repo.add_item(
            Organization(
                row_id=1000,
                name="test_org",
                org_id="test_org_id",
                org_uuid="test_org_uuid",
                type="organization",
                owner="dummyuser@dummy.io",
                owner_name="Test Owner",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                address=[],
                metadata_ipfs_hash="#dummyhashdummyhash"
            )
        )
        org_repo.add_item(
            OrganizationReviewWorkflow(
                org_row_id=1000,
                status=OrganizationStatus.APPROVAL_PENDING.value,
                transaction_hash="",
                wallet_address="",
                created_by="",
                updated_by="",
                approved_by="",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            ))
        org_repo.add_item(
            OrganizationMember(
                org_uuid="test_org_uuid",
                role="MEMBER",
                username="dummy_user5@dummy.io",
                address=None,
                status=OrganizationMemberStatus.PENDING.value,
                transaction_hash="",
                invite_code="zxcvbnmqwertyuioasdfghjkl",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        event = {"requestContext": {
            "authorizer": {
                "claims": {
                    "email": "dummy_user5@dummy.io"
                }
            }
        }, "httpMethod": "GET", "queryStringParameters": {"invite_code": "zxcvbnmqwertyuioasdfghjkl"}}
        response = verify_code(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"] == "OK")

    def test_accept_invitation(self):
        self.tearDown()
        org_repo.add_item(
            Organization(
                row_id=1000,
                name="test_org",
                org_id="test_org_id",
                org_uuid="test_org_uuid",
                type="organization",
                owner="dummyuser@dummy.io",
                owner_name="Test Owner",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                address=[],
                metadata_ipfs_hash="#dummyhashdummyhash"
            )
        )
        org_repo.add_item(
            OrganizationReviewWorkflow(
                org_row_id=1000,
                status=OrganizationStatus.APPROVAL_PENDING.value,
                transaction_hash="",
                wallet_address="",
                created_by="",
                updated_by="",
                approved_by="",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            ))
        org_repo.add_item(
            OrganizationMember(
                org_uuid="test_org_uuid",
                role="MEMBER",
                username="dummy_user6@dummy.io",
                address=None,
                status=OrganizationMemberStatus.PENDING.value,
                transaction_hash="",
                invite_code="zxcvbnmqwertyuioasdfghjkl",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        event = {"httpMethod": "POST",
                 "requestContext": {
                     "authorizer": {
                         "claims": {
                             "email": "dummy_user6@dummy.io"
                         }
                     }
                 },
                 "body": json.dumps({
                     "invite_code": "zxcvbnmqwertyuioasdfghjkl",
                     "wallet_address": "0x3Bb9b2499c283cec176e7C707Ecb495B7a961ebf"
                 })}
        response = register_member(event=event, context=None)
        assert (response["statusCode"] == 201)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"] == "OK")

    def test_publish_members(self):
        self.tearDown()
        org_repo.add_item(
            Organization(
                row_id=1000,
                name="test_org",
                org_id="test_org_id",
                org_uuid="test_org_uuid",
                type="organization",
                owner="dummyuser@dummy.io",
                owner_name="Test Owner",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                address=[],
                metadata_ipfs_hash="#dummyhashdummyhash"
            )
        )
        org_repo.add_item(
            OrganizationReviewWorkflow(
                org_row_id=1000,
                status=OrganizationStatus.APPROVAL_PENDING.value,
                transaction_hash="",
                wallet_address="",
                created_by="",
                updated_by="",
                approved_by="",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            ))
        org_repo.add_item(
            OrganizationMember(
                org_uuid="test_org_uuid",
                role="MEMBER",
                username="dummy_user7@dummy.io",
                address="0x3Bb9b2499c283cec176e7C707Ecb495B7a961ebg",
                status=OrganizationMemberStatus.ACCEPTED.value,
                transaction_hash="",
                invite_code="qwertyuiolkjhgfdsa",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        event = {
            "httpMethod": "POST",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummyuser@dummy.io"
                    }
                }
            },
            "pathParameters": {"org_id": "test_org_uuid"},
            "body": json.dumps({
                "transaction_hash": "0x4df7db342f580df53191a2f13db830c00145b92e3bc8e7e8e054813ce320b089",
                "members": [
                    {
                        "username": "dummy_user7@dummy.io",
                        "address": "0x3Bb9b2499c283cec176e7C707Ecb495B7a961ebg",
                        "role": "MEMBER",
                        "status": "ACCEPTED"
                    }]
            })

        }
        response = publish_members(event=event, context=None)
        assert (response["statusCode"] == 201)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"] == "OK")

    def test_delete_member(self):
        self.tearDown()
        org_repo.add_item(
            Organization(
                row_id=1000,
                name="test_org",
                org_id="test_org_id",
                org_uuid="test_org_uuid",
                type="organization",
                owner="dummyuser@dummy.io",
                owner_name="Test Owner",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                address=[],
                metadata_ipfs_hash="#dummyhashdummyhash"
            )
        )
        org_repo.add_item(
            OrganizationReviewWorkflow(
                org_row_id=1000,
                status=OrganizationStatus.APPROVAL_PENDING.value,
                transaction_hash="",
                wallet_address="",
                created_by="",
                updated_by="",
                approved_by="",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            ))
        org_repo.add_item(
            OrganizationMember(
                org_uuid="test_org_uuid",
                role="MEMBER",
                username="dummy_user8@dummy.io",
                address="0x3Bb9b2499c283cec176e7C707Ecb495B7a961ebg",
                status=OrganizationMemberStatus.PUBLISHED.value,
                transaction_hash="0x4df7db342f580df53191a2f13db830c00145b92e3bc8e7e8e054813ce420b089",
                invite_code="rtyfghasdfghjkl",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        event = {
            "httpMethod": "POST",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummyuser@dummy.io"
                    }
                }
            },
            "pathParameters": {"org_id": "test_org_uuid"},
            "body": json.dumps({
                "members": [
                    {
                        "username": "dummy_user8@dummy.io"
                    }]
            })
        }
        response = delete_members(event=event, context=None)
        assert (response["statusCode"] == 201)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def tearDown(self):
        org_repo.session.query(OrganizationReviewWorkflow).delete()
        org_repo.session.query(OrganizationMember).delete()
        org_repo.session.query(Organization).delete()
        org_repo.session.commit()
