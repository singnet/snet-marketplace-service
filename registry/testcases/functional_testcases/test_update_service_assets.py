import json
from datetime import datetime as dt
from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

from registry.application.handlers.service_handlers import update_service_assets, update_demo_component_build_status, \
    get_code_build_status_for_service
from registry.constants import OrganizationMemberStatus, ServiceStatus
from registry.constants import Role
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository
from registry.infrastructure.models import Organization as OrganizationDBModel
from registry.infrastructure.models import OrganizationMember as OrganizationMemberDBModel
from registry.infrastructure.models import OrganizationState as OrganizationStateDBModel
from registry.infrastructure.models import Service as ServiceDBModel
from registry.infrastructure.models import ServiceGroup as ServiceGroupDBModel
from registry.infrastructure.models import ServiceReviewHistory as ServiceReviewHistoryDBModel
from registry.infrastructure.models import ServiceState as ServiceStateDBModel

org_repo = OrganizationPublisherRepository()
service_repo = ServicePublisherRepository()


class TestService(TestCase):
    def setUp(self):
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
            }
        ]
        org_repo.add_all_items(
            [OrganizationMemberDBModel(
                username=member["username"],
                org_uuid="test_org_uuid",
                role=Role.MEMBER.value,
                address=member["address"],
                status=OrganizationMemberStatus.ACCEPTED.value,
                transaction_hash="0x123",
                invite_code=str(uuid4()),
                invited_on=dt.utcnow(),
                updated_on=dt.utcnow()
            ) for member in new_org_members])
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
                assets={
                    "demo_files": {
                        "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/component/20210228000436_component.zip",
                        "ipfs_hash": "QmUKfyv5c8Ru93xyxTcXGswnNzuBTCBU9NGjMV7SMwLSgy",
                        "build_id": "sample_build_id"
                    },
                    "hero_image": {
                        "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/assets/20210127060152_asset.png",
                        "ipfs_hash": "QmdSh54XcNPJo8v89LRFDN5FAoGL92mn174rKFzoHwUCM1/20210127060152_asset.png"
                    },
                    "proto_files": {
                        "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/proto/20210131042033_proto_files.zip",
                        "ipfs_hash": "QmUKfyv5c8Ru93xyxTcXGswnNzuBTCBU9NGjMV7SMwLSgy"
                    }
                },
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

    def test_validate_hero_image(self):
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {
                            "name": "ropsten-marketplace-service-assets",
                            "ownerIdentity": {
                                "principalId": "A1AEOFBS4PX33"
                            },
                            "arn": "arn:aws:s3:::ropsten-marketplace-service-assets"
                        },
                        "object": {
                            "key": "test_org_uuid/services/test_service_uuid/assets/20210127060155_asset.jpeg",
                            "size": 6949,
                            "eTag": "c80928fa72a7ceb972b54a214c2181b3",
                            "sequencer": "0060CCFC79D1D7CCDF"
                        }
                    }
                }
            ]
        }
        response = update_service_assets(event=event, context=None)
        assert response["statusCode"] == 200
        service = ServicePublisherRepository().get_service_for_given_service_uuid(org_uuid="test_org_uuid",
                                                                                  service_uuid="test_service_uuid")
        print(service.to_dict())
        assert service.assets == {
            "demo_files": {
                "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/component/20210228000436_component.zip",
                "build_id": "sample_build_id",
                "ipfs_hash": "QmUKfyv5c8Ru93xyxTcXGswnNzuBTCBU9NGjMV7SMwLSgy"
            },
            "hero_image": {
                "url": "https://ropsten-marketplace-service-assets.s3.us-east-1.amazonaws.com/test_org_uuid/services/test_service_uuid/assets/20210127060155_asset.jpeg"},
            "proto_files": {
                "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/proto/20210131042033_proto_files.zip",
                "ipfs_hash": "QmUKfyv5c8Ru93xyxTcXGswnNzuBTCBU9NGjMV7SMwLSgy"}
        }

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_validate_proto(self, mock_proto_compile_response):
        mock_proto_compile_response.return_value = {"statusCode": 200}
        event = {"Records":
                     [{"eventVersion": "2.1", "eventSource": "aws:s3", "awsRegion": "us-east-1", "eventTime": "2021-06-18T11:49:39.596Z",
                       "eventName": "ObjectCreated:Put",
                       "userIdentity": {"principalId": "AWS:AROAIJDMM5CI656XV7AOY:common-utility-rt-v2-upload"},
                       "requestParameters": {"sourceIPAddress": "18.210.102.181"},
                       "responseElements": {"x-amz-request-id": "CK234N3ZN84W1TZ5",
                                            "x-amz-id-2": "9lHUaMDKbuCB9C6YnI6CjJuuWWhSiunQgXSnHHDK1+6ETaAjq95qSuYsqQGUhfbSOGStTohI3qiWpCjNrg36mFh4uTvh+PdW"},
                       "s3": {"s3SchemaVersion": "1.0", "configurationId": "31f60a9a-a853-406c-b697-495098f6257d",
                              "bucket": {"name": "ropsten-marketplace-service-assets", "ownerIdentity": {"principalId": "A1AEOFBS4PX33"},
                                         "arn": "arn:aws:s3:::ropsten-marketplace-service-assets"},
                              "object": {"key": "test_org_uuid/services/test_service_uuid/proto/20210618114940_proto_files.zip",
                                         "size": 374, "eTag": "57a5f8d4130aab3172c6aac7b898c4d7", "sequencer": "0060CC8854D23C18E7"}}}]}
        response = update_service_assets(event=event, context=None)
        service = ServicePublisherRepository().get_service_for_given_service_uuid(org_uuid="test_org_uuid",
                                                                                  service_uuid="test_service_uuid")
        assert response["statusCode"] == 200
        assert service.assets == {"demo_files": {"url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/component/20210228000436_component.zip", "build_id": "sample_build_id", "ipfs_hash": "QmUKfyv5c8Ru93xyxTcXGswnNzuBTCBU9NGjMV7SMwLSgy"},
                                  "hero_image": {"url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/assets/20210127060152_asset.png", "ipfs_hash": "QmdSh54XcNPJo8v89LRFDN5FAoGL92mn174rKFzoHwUCM1/20210127060152_asset.png"},
                                  "proto_files": {"url": "https://ropsten-marketplace-service-assets.s3.us-east-1.amazonaws.com/test_org_uuid/services/test_service_uuid/proto/20210618114940_proto_files.zip", "status": "SUCCEEDED"}
                                  }

    def test_demo_component_build_status_update(self):
        event = {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid", "build_status": "0",
                 "build_id": "sample_build_id", "filename": "incorrect_name.zip"}
        response = update_demo_component_build_status(event=event, context=None)
        assert response["statusCode"] == 200
        service = ServicePublisherRepository().get_service_for_given_service_uuid(org_uuid="test_org_uuid",
                                                                                  service_uuid="test_service_uuid")

        assert service.assets == {
            "demo_files": {
                "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/component/20210228000436_component.zip",
                "ipfs_hash": "QmUKfyv5c8Ru93xyxTcXGswnNzuBTCBU9NGjMV7SMwLSgy",
                "build_id": "sample_build_id"
            },
            "hero_image": {
                "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/assets/20210127060152_asset.png",
                "ipfs_hash": "QmdSh54XcNPJo8v89LRFDN5FAoGL92mn174rKFzoHwUCM1/20210127060152_asset.png"
            },
            "proto_files": {
                "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/proto/20210131042033_proto_files.zip",
                "ipfs_hash": "QmUKfyv5c8Ru93xyxTcXGswnNzuBTCBU9NGjMV7SMwLSgy"
            }
        }

        event = {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid", "build_status": "0",
                 "build_id": "sample_build_id", "filename": "20210228000436_component.zip"}
        response = update_demo_component_build_status(event=event, context=None)
        assert response["statusCode"] == 200
        service = ServicePublisherRepository().get_service_for_given_service_uuid(org_uuid="test_org_uuid",
                                                                                  service_uuid="test_service_uuid")
        assert service.assets == {
            "demo_files": {
                "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/component/20210228000436_component.zip",
                "status": "FAILED", "build_id": "sample_build_id",
                "ipfs_hash": "QmUKfyv5c8Ru93xyxTcXGswnNzuBTCBU9NGjMV7SMwLSgy"},
            "hero_image": {
                "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/assets/20210127060152_asset.png",
                "ipfs_hash": "QmdSh54XcNPJo8v89LRFDN5FAoGL92mn174rKFzoHwUCM1/20210127060152_asset.png"},
            "proto_files": {
                "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/proto/20210131042033_proto_files.zip",
                "ipfs_hash": "QmUKfyv5c8Ru93xyxTcXGswnNzuBTCBU9NGjMV7SMwLSgy"}
        }

        service_state = ServicePublisherRepository().get_service_state(
            status=ServiceStatus.CHANGE_REQUESTED.value)
        assert service_state[0].org_uuid == "test_org_uuid"
        assert service_state[0].service_uuid == "test_service_uuid"

        ServicePublisherRepository().update_service_status(service_uuid_list=["test_service_uuid"],
                                                           prev_state=ServiceStatus.CHANGE_REQUESTED.value,
                                                           next_state=ServiceStatus.APPROVAL_PENDING.value)
        event = {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid", "build_status": "1",
                 "build_id": "sample_build_id", "filename": "20210228000436_component.zip"}
        response = update_demo_component_build_status(event=event, context=None)
        assert response["statusCode"] == 200
        service = ServicePublisherRepository().get_service_for_given_service_uuid(org_uuid="test_org_uuid",
                                                                                  service_uuid="test_service_uuid")
        assert service.assets == {
            "demo_files": {
                "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/component/20210228000436_component.zip",
                "status": "SUCCEEDED", "build_id": "sample_build_id",
                "ipfs_hash": "QmUKfyv5c8Ru93xyxTcXGswnNzuBTCBU9NGjMV7SMwLSgy"},
            "hero_image": {
                "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/assets/20210127060152_asset.png",
                "ipfs_hash": "QmdSh54XcNPJo8v89LRFDN5FAoGL92mn174rKFzoHwUCM1/20210127060152_asset.png"},
            "proto_files": {
                "url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/proto/20210131042033_proto_files.zip",
                "ipfs_hash": "QmUKfyv5c8Ru93xyxTcXGswnNzuBTCBU9NGjMV7SMwLSgy"}
        }

    @patch("common.boto_utils.BotoUtils.trigger_code_build")
    def test_validate_demo_component(self, mock_code_build):
        mock_code_build.return_value = {"build": {"id": "test_build_id"}}
        event = {"Records": [{"eventVersion": "2.1", "eventSource": "aws:s3", "awsRegion": "us-east-1", "eventTime": "2021-06-16T15:49:00.312Z", "eventName": "ObjectCreated:Put", "userIdentity": {"principalId": "AWS:AIDAXYSEM4MOPXXLSNUMO"}, "requestParameters": {"sourceIPAddress": "117.213.142.222"}, "responseElements": {"x-amz-request-id": "XNESWXSYFNZA8HKK", "x-amz-id-2": "ir/3JEviL89t07LOtI2+oQE6X+EMtHWFOWyojXXNkNF/p2ZcsgeBg9X81dbZA2sj4gJw/CI8mhEfyJNcXdpPhkjcRqBYpwRHYH7vzMvrRsU="}, "s3": {"s3SchemaVersion": "1.0", "configurationId": "b2733823-1355-4982-abdd-8f14cb7ddba4", "bucket": {"name": "ropsten-marketplace-service-assets", "ownerIdentity": {"principalId": "A1AEOFBS4PX33"}, "arn": "arn:aws:s3:::ropsten-marketplace-service-assets"}, "object": {"key": "test_org_uuid/services/test_service_uuid/component/example_service_component.zip", "size": 5248, "eTag": "54ea849194040b43601f44ed53e5dc1b", "sequencer": "0060CA1D6C80321671"}}}]}
        response = update_service_assets(event=event, context=None)
        service = ServicePublisherRepository().get_service_for_given_service_uuid(org_uuid="test_org_uuid",
                                                                                  service_uuid="test_service_uuid")
        assert response["statusCode"] == 200
        assert json.loads(response["body"])["data"]["build_id"] == "test_build_id"
        assert service.assets == {
            "demo_files": {"url": "https://ropsten-marketplace-service-assets.s3.us-east-1.amazonaws.com/test_org_uuid/services/test_service_uuid/component/example_service_component.zip", "status": "PENDING", "build_id": "test_build_id"},
            "hero_image": {"url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/assets/20210127060152_asset.png", "ipfs_hash": "QmdSh54XcNPJo8v89LRFDN5FAoGL92mn174rKFzoHwUCM1/20210127060152_asset.png"},
            "proto_files": {"url": "https://marketplace-registry-assets.s3.amazonaws.com/6509581150c8446e8a73b3fa71ebdb69/services/05676ad531cd40a889841ff1f3c5608b/proto/20210131042033_proto_files.zip", "ipfs_hash": "QmUKfyv5c8Ru93xyxTcXGswnNzuBTCBU9NGjMV7SMwLSgy"}
        }

    @patch("common.boto_utils.BotoUtils.get_code_build_details")
    def test_get_code_build_status(self, mock_build_response):
        mock_build_response.return_value = {
            "builds": [
                {
                    "id": "sample_build_id",
                    "arn": "arn:aws:codebuild:us-east-1:533793137436:build/ropstenstagingv2codebuildtr-LwN9IM20ho2d:08444f51-ed99-47d8-ba08-565ae1dc28ef",
                    "currentPhase": "COMPLETED",
                    "buildStatus": "SUCCEEDED"
                }
            ]
        }
        event = {"pathParameters": {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid"}}
        response = get_code_build_status_for_service(event=event, context=None)
        assert (response["statusCode"] == 200)
        body = json.loads(response["body"])
        assert body["data"]["build_status"] == "SUCCEEDED"

    def tearDown(self):
        org_repo.session.query(OrganizationStateDBModel).delete()
        org_repo.session.query(OrganizationMemberDBModel).delete()
        org_repo.session.query(OrganizationDBModel).delete()
        org_repo.session.query(ServiceDBModel).delete()
        org_repo.session.query(ServiceGroupDBModel).delete()
        org_repo.session.query(ServiceStateDBModel).delete()
        org_repo.session.query(ServiceReviewHistoryDBModel).delete()
        org_repo.session.commit()

