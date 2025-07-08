import json
from unittest import TestCase
from unittest.mock import patch

from contract_api.domain.models.channel import NewChannelDomain
from contract_api.domain.models.org_group import NewOrgGroupDomain
from contract_api.domain.models.organization import NewOrganizationDomain
from contract_api.domain.models.service import NewServiceDomain

from contract_api.infrastructure.repositories.channel_repository import ChannelRepository
from contract_api.infrastructure.repositories.organization_repository import OrganizationRepository
from contract_api.application.handlers.organization_handlers import *
from contract_api.infrastructure.repositories.service_repository import ServiceRepository


class TestOrganizations(TestCase):
    channel_id = 123

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
        self.org_repository.session.commit()
        self.service_repository.upsert_service(
            NewServiceDomain(
                org_id = "test_org_id",
                service_id = "test_service_id",
                hash_uri = "",
                is_curated = True
            )
        )
        self.service_repository.session.commit()

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
        self.service_repository.upsert_service(
            NewServiceDomain(
                org_id = "test_org_id_2",
                service_id = "test_service_id_2",
                hash_uri = "",
                is_curated = True
            )
        )
        self.service_repository.session.commit()
        self.org_repository.create_org_groups(
            [NewOrgGroupDomain(
                org_id = "test_org_id",
                group_id = "NSf/28//MmwM+ktwr1gO0vVFoWqvctAT+Qko6lO3Xzo=",
                group_name = "default_group",
                payment = {"payment_address": "0x4DD0668f583c92b006A81743c9704Bd40c876fDE"}
            )]
        )
        self.org_repository.session.commit()

    def tearDown(self):
        self.org_repository.delete_organization("test_org_id")
        self.org_repository.delete_organization("test_org_id_2")

    def test_get_organizations(self):
        response = get_all_organizations(None, None)

        assert response["statusCode"] == 200

        data = json.loads(response["body"])["data"]

        expected_org_1 = {
            'org_id': 'test_org_id',
            'organization_name': 'test_org_name',
            'owner_address': '0x6E7BaCcc00D69eab750eDf661D831cd2c7f3A4DF',
            'org_metadata_uri': '',
            'org_assets_url': {'hero_image': 'test_url'},
            'is_curated': True,
            'description': {},
            'assets_hash': {},
            'contacts': {},
            'org_email': 'NULL'
        }
        expected_org_2 = {
            'org_id': 'test_org_id_2',
            'organization_name': 'test_org_name_2',
            'owner_address': '0x6E7BaCcc00D69eab750eDf661D831cd2c7f3A4DF',
            'org_metadata_uri': '',
            'org_assets_url': {'hero_image': 'test_url'},
            'is_curated': True,
            'description': {},
            'assets_hash': {},
            'contacts': {},
            'org_email': 'NULL'
        }

        assert data[-2] == expected_org_1
        assert data[-1] == expected_org_2

    def test_get_group(self):
        event = {
            "org_id": "test_org_id",
            "group_id": "NSf/28//MmwM+ktwr1gO0vVFoWqvctAT+Qko6lO3Xzo="
        }
        response = get_group(event, None)

        assert response["statusCode"] == 200

        data = json.loads(response["body"])["data"]