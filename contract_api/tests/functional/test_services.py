import json
from datetime import datetime, UTC
from unittest import TestCase
from unittest.mock import patch

from contract_api.application.handlers.service_handlers import *
from contract_api.domain.factory.service_factory import ServiceFactory
from contract_api.domain.models.organization import NewOrganizationDomain
from contract_api.domain.models.service import NewServiceDomain
from contract_api.domain.models.service_endpoint import NewServiceEndpointDomain
from contract_api.domain.models.service_media import NewServiceMediaDomain
from contract_api.domain.models.service_tag import NewServiceTagDomain
from contract_api.infrastructure.repositories.organization_repository import OrganizationRepository
from contract_api.infrastructure.repositories.service_repository import ServiceRepository
from contract_api.tests.functional.service_metadata_for_test import service_metadata_1, service_metadata_2


class TestServices(TestCase):
    def setUp(self):
        self.org_repository = OrganizationRepository()
        self.service_repository = ServiceRepository()
        self.org_repository.upsert_organization(
            NewOrganizationDomain(
                org_id = "test_org_id",
                organization_name = "test_org_name",
                owner_address = "0x6E7BaCcc00D69eab750eDf661D831cd2c7f3A4DF",
                org_metadata_uri = "",
                org_assets_url = {"hero_image": "test_url"},
                is_curated = True,
                description = {},
                assets_hash = {},
                contacts = {},
            )
        )
        self.org_repository.upsert_organization(
            NewOrganizationDomain(
                org_id = "test_org_id_2",
                organization_name = "test_org_name_2",
                owner_address = "0x6E7BaCcc00D69eab750eDf661D831cd2c7f3A4DF",
                org_metadata_uri = "",
                org_assets_url = {"hero_image": "test_url"},
                is_curated = True,
                description = {},
                assets_hash = {},
                contacts = {},
            )
        )
        self.org_repository.session.commit()


        service_1 = self.service_repository.upsert_service(
            NewServiceDomain(
                org_id = "test_org_id",
                service_id = "test_service_id",
                hash_uri = "",
                is_curated = True
            )
        )
        self.service_repository.upsert_service_metadata(
            ServiceFactory.service_metadata_from_metadata_dict(
                metadata_dict = service_metadata_1,
                service_row_id = service_1.row_id,
                org_id = service_1.org_id,
                service_id = service_1.service_id,
                assets_url = service_metadata_1.get("assets", {}),
                model_hash = service_metadata_1.get("service_api_source", ""),
                type = service_metadata_1.get("service_type", ""),
                **service_metadata_1["service_description"]
            )
        )
        self.service_repository.upsert_service_endpoint(
            NewServiceEndpointDomain(
                service_row_id = service_1.row_id,
                org_id = service_1.org_id,
                service_id = service_1.service_id,
                group_id = service_metadata_1["groups"][0]["group_id"],
                endpoint = service_metadata_1["groups"][0]["endpoints"][0],
                is_available = True,
                last_check_timestamp = datetime.now(UTC)
            )
        )
        service_media_item = service_metadata_1["media"][0]
        self.service_repository.upsert_service_media(
            NewServiceMediaDomain(
                service_row_id = service_1.row_id,
                org_id = service_1.org_id,
                service_id = service_1.service_id,
                url = service_media_item.get("url", ""),
                order = service_media_item.get("order", 0),
                file_type = service_media_item.get("file_type", ""),
                asset_type = service_media_item.get("asset_type", ""),
                alt_text = service_media_item.get("alt_text", ""),
                hash_uri = ""
            )
        )
        for tag_name in ["tag1", "tag2", "tag3"]:
            self.service_repository.create_service_tag(
                NewServiceTagDomain(
                    service_row_id = service_1.row_id,
                    org_id = service_1.org_id,
                    service_id = service_1.service_id,
                    tag_name = tag_name
                )
            )

        self.service_repository.session.commit()

        service_2 = self.service_repository.upsert_service(
            NewServiceDomain(
                org_id = "test_org_id_2",
                service_id = "test_service_id_2",
                hash_uri = "",
                is_curated = True
            )
        )
        self.service_repository.upsert_service_metadata(
            ServiceFactory.service_metadata_from_metadata_dict(
                metadata_dict = service_metadata_2,
                service_row_id = service_2.row_id,
                org_id = service_2.org_id,
                service_id = service_2.service_id,
                assets_url = service_metadata_2.get("assets", {}),
                model_hash = service_metadata_2.get("service_api_source", ""),
                type = service_metadata_2.get("service_type", ""),
                **service_metadata_2["service_description"]
            )
        )
        self.service_repository.upsert_service_endpoint(
            NewServiceEndpointDomain(
                service_row_id = service_2.row_id,
                org_id = service_2.org_id,
                service_id = service_2.service_id,
                group_id = service_metadata_2["groups"][0]["group_id"],
                endpoint = service_metadata_2["groups"][0]["endpoints"][0],
                is_available = True,
                last_check_timestamp = datetime.now(UTC)
            )
        )
        service_media_item = service_metadata_2["media"][0]
        self.service_repository.upsert_service_media(
            NewServiceMediaDomain(
                service_row_id = service_2.row_id,
                org_id = service_2.org_id,
                service_id = service_2.service_id,
                url = service_media_item.get("url", ""),
                order = service_media_item.get("order", 0),
                file_type = service_media_item.get("file_type", ""),
                asset_type = service_media_item.get("asset_type", ""),
                alt_text = service_media_item.get("alt_text", ""),
                hash_uri = ""
            )
        )
        for tag_name in ["tag2", "tag3", "tag4"]:
            self.service_repository.create_service_tag(
                NewServiceTagDomain(
                    service_row_id = service_2.row_id,
                    org_id = service_2.org_id,
                    service_id = service_2.service_id,
                    tag_name = tag_name
                )
            )

        self.service_repository.session.commit()

    def tearDown(self):
        self.org_repository.delete_organization("test_org_id")
        self.org_repository.delete_organization("test_org_id_2")

    def test_get_service_filters_tags(self):
        event = {
            "queryStringParameters": {
                "attribute": "tagName",
            }
        }

        response = get_service_filters(event, None)

        assert response["statusCode"] == 200

        data = json.loads(response["body"])["data"]
        expected_result = {"values": ["tag1", "tag2", "tag3", "tag4"]}

        self.assertDictEqual(data, expected_result)

    def test_get_service_filters_orgs(self):
        event = {
            "queryStringParameters": {
                "attribute": "orgId",
            }
        }

        response = get_service_filters(event, None)

        assert response["statusCode"] == 200

        data = json.loads(response["body"])["data"]
        expected_result = {"values": {"test_org_id": "test_org_name", "test_org_id_2": "test_org_name_2"}}

        self.assertDictEqual(data, expected_result)

    def test_get_services_with_filters(self):
        event = {
            "body": json.dumps({
                "limit": 36,
                "page": 1,
                "sort": "rating",
                "order": "asc",
                "q": "",
                "filter": {
                    "orgId": ["test_org_id"],
                    "tagName": ["tag1"],
                    "onlyAvailable": True
                }
            })
        }

        response = get_services(event, None)

        assert response["statusCode"] == 200
        data = json.loads(response["body"])["data"]
        expected_result = {
          "totalCount": 1,
          "services": [
            {
              "orgId": "test_org_id",
              "organizationName": "test_org_name",
              "serviceId": "test_service_id",
              "displayName": "test_service_id",
              "rating": 0,
              "numberOfRatings": 0,
              "shortDescription": "123",
              "isAvailable": True,
              "orgImageUrl": "test_url",
              "serviceImageUrl": "https://dev-fet-marketplace-service-assets.s3.us-east-1.amazonaws.com/a32d4af601344d27a631e5d2a3f612cb/services/a7000a8e9a09496c826086fd14a09ca2/assets/20250619074449_asset.png"
            }
          ]
        }

        self.assertDictEqual(data, expected_result)

    def test_get_services_without_filters(self):
        event = {
            "body": json.dumps({
                "limit": 36,
                "page": 1,
                "sort": "rating",
                "order": "asc",
                "q": ""
            })
        }

        response = get_services(event, None)

        assert response["statusCode"] == 200
        data = json.loads(response["body"])["data"]
        print(data)
        expected_result = {
          "totalCount": 2,
          "services": [
            {
              "orgId": "test_org_id",
              "organizationName": "test_org_name",
              "serviceId": "test_service_id",
              "displayName": "test_service_id",
              "rating": 0,
              "numberOfRatings": 0,
              "shortDescription": "123",
              "isAvailable": True,
              "orgImageUrl": "test_url",
              "serviceImageUrl": "https://dev-fet-marketplace-service-assets.s3.us-east-1.amazonaws.com/a32d4af601344d27a631e5d2a3f612cb/services/a7000a8e9a09496c826086fd14a09ca2/assets/20250619074449_asset.png"
            },
            {
              "orgId": "test_org_id_2",
              "organizationName": "test_org_name_2",
              "serviceId": "test_service_id_2",
              "displayName": "test_service_id_2",
              "rating": 0,
              "numberOfRatings": 0,
              "shortDescription": "123",
              "isAvailable": True,
              "orgImageUrl": "test_url",
              "serviceImageUrl": "https://dev-fet-marketplace-service-assets.s3.us-east-1.amazonaws.com/a32d4af601344d27a631e5d2a3f612cb/services/a7000a8e9a09496c826086fd14a09ca2/assets/20250619074449_asset.png"
            }
          ]
        }

        self.maxDiff = None
        self.assertDictEqual(data, expected_result)

    def test_get_service(self):
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            }
        }
        response = get_service(event, None)

        assert response["statusCode"] == 200

        data = json.loads(response["body"])["data"]
        print(data)

        expected_result = {
          "orgId": "test_org_id",
          "serviceId": "test_service_id",
          "organizationName": "test_org_name",
          "orgImageUrl": "test_url",
          "supportContacts": {
            "email": "",
            "phone": ""
          },
          "displayName": "test_service_id",
          "description": "123",
          "shortDescription": "123",
          "url": "https://totsky.ee/",
          "rating": 0.0,
          "numberOfRatings": 0,
          "contributors": [
            "Vjatseslav"
          ],
          "media": [
            {
              "url": "https://dev-fet-marketplace-service-assets.s3.us-east-1.amazonaws.com/a32d4af601344d27a631e5d2a3f612cb/services/a7000a8e9a09496c826086fd14a09ca2/assets/20250619074449_asset.png",
              "assetType": "hero_image"
            }
          ],
          "tags": [
            "tag1",
            "tag2",
            "tag3"
          ],
          "isAvailable": False,
          "groups": [],
          "demoComponentRequired": True
        }

        self.maxDiff = None
        self.assertDictEqual(data, expected_result)

    def test_curate_service(self):
        event = {
            "queryStringParameters": {
                "org_id": "test_org_id",
                "service_id": "test_service_id",
                "curate": "false"
            }
        }
        response = curate_service(event, None)

        assert response["statusCode"] == 201
        assert not self.service_repository.service_curated("test_org_id", "test_service_id")

        event["queryStringParameters"]["curate"] = "true"
        response = curate_service(event, None)

        assert response["statusCode"] == 201
        assert self.service_repository.service_curated("test_org_id", "test_service_id")

    @patch("contract_api.application.services.service_service.ServiceService._publish_demo_component")
    def test_a_save_offchain_attribute(self, publish_demo_component):
        publish_demo_component.return_value = "new_test_url"
        event = {
            "pathParameters": {
                "org_id": "test_org_id",
                "service_id": "test_service_id"
            },
            "body": json.dumps({
                "demo_component": {
                    "demo_component_url": "test_url",
                    "demo_component_required": 1,
                    "demo_component_status": "PENDING",
                    "change_in_demo_component": 1
                }
            })
        }

        response = save_offchain_attribute(event, None)

        assert response["statusCode"] == 200

        data = json.loads(response["body"])["data"]
        print(data)

        expected_result = {
            "org_id": "test_org_id",
            "service_id": "test_service_id",
            "attributes": {
                "demo_component_required": "1",
                "demo_component_status": "PENDING",
                "demo_component_url": "new_test_url"
            }
        }

        self.assertDictEqual(data, expected_result)

    def test_b_get_offchain_attribute(self):
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            }
        }

        response = get_offchain_attribute(event, None)

        assert response["statusCode"] == 200

        data = json.loads(response["body"])["data"]

        expected_result = {
            "hash_uri": "", 
            "demo_component": {
                "demo_component_required": "1", 
                "demo_component_status": "PENDING", 
                "demo_component_url": "new_test_url"
            }
        }
        del data["demo_component"]["demo_component_last_modified"]

        self.assertDictEqual(data, expected_result)

    def test_update_service_rating(self):
        event = {
            "pathParameters": {
                "org_id": "test_org_id",
                "service_id": "test_service_id"
            },
            "body": json.dumps({
                "rating": 3.5,
                "total_users_rated": 5
            })
        }

        response = update_service_rating(event, None)

        assert response["statusCode"] == 200

        service_metadata = self.service_repository.get_service_metadata("test_org_id", "test_service_id")

        expected_result = {
            "rating": 3.5,
            "total_users_rated": 5
        }

        self.assertDictEqual(service_metadata.service_rating, expected_result)

