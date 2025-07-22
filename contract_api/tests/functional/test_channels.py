import json
from unittest import TestCase
from unittest.mock import patch

from contract_api.domain.models.channel import NewChannelDomain
from contract_api.domain.models.org_group import NewOrgGroupDomain
from contract_api.domain.models.organization import NewOrganizationDomain

from contract_api.infrastructure.repositories.channel_repository import ChannelRepository
from contract_api.infrastructure.repositories.organization_repository import OrganizationRepository
from contract_api.application.handlers.channel_handlers import *


class TestChannels(TestCase):
    channel_id = 123

    def setUp(self):
        self.channel_repository = ChannelRepository()
        self.org_repository = OrganizationRepository()
        self.channel_repository.upsert_channel(
            NewChannelDomain(
                channel_id=self.channel_id,
                sender="0x6E7BaCcc00D69eab750eDf661D831cd2c7f3A4DF",
                signer="0x6E7BaCcc00D69eab750eDf661D831cd2c7f3A4DF",
                recipient="0x4DD0668f583c92b006A81743c9704Bd40c876fDE",
                nonce=0,
                expiration=123456789,
                balance_in_cogs=10,
                group_id="NSf/28//MmwM+ktwr1gO0vVFoWqvctAT+Qko6lO3Xzo="
            )
        )
        # with self.org_repository.session.begin():
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
        self.channel_repository.delete_channel(self.channel_id)
        self.org_repository.delete_organization("test_org_id")

    def test_get_channels(self):
        event = {
            "queryStringParameters": {
                "walletAddress": "0x6E7BaCcc00D69eab750eDf661D831cd2c7f3A4DF",
            }
        }

        response = get_channels(event = event, context = None)
        assert response["statusCode"] == 200

        data = json.loads(response["body"])["data"]
        assert data["organizations"][0]["orgId"] == "test_org_id"
        assert data["organizations"][0]["orgName"] == "test_org_name"
        assert data["organizations"][0]["heroImage"] == "test_url"
        assert list(data["organizations"][0]["channels"].items())[0] == (str(self.channel_id), 10)

    def test_get_group_channels(self):
        event = {
            "queryStringParameters": {
                "user_address": "0x6E7BaCcc00D69eab750eDf661D831cd2c7f3A4DF",
                "org_id": "test_org_id",
                "group_id": "NSf/28//MmwM+ktwr1gO0vVFoWqvctAT+Qko6lO3Xzo="
            }
        }

        response = get_group_channels(event = event, context = None)
        assert response["statusCode"] == 200

        real_data = json.loads(response["body"])["data"]
        expected_data = {
            "user_address": "0x6E7BaCcc00D69eab750eDf661D831cd2c7f3A4DF",
            "org_id": "test_org_id",
            "group_id": "NSf/28//MmwM+ktwr1gO0vVFoWqvctAT+Qko6lO3Xzo=",
            "channels": [
                {
                    "channel_id": 123,
                    "sender": "0x6E7BaCcc00D69eab750eDf661D831cd2c7f3A4DF",
                    "signer": "0x6E7BaCcc00D69eab750eDf661D831cd2c7f3A4DF",
                    "recipient": "0x4DD0668f583c92b006A81743c9704Bd40c876fDE",
                    "group_id": "NSf/28//MmwM+ktwr1gO0vVFoWqvctAT+Qko6lO3Xzo=",
                    "balance_in_cogs": 10,
                    "nonce": 0,
                    "expiration": 123456789,
                    "pending": 0,
                    "consumed_balance": 0
                }
            ]
        }

        self.assertDictEqual(real_data, expected_data)

    def test_update_consumed_balance(self):
        event = {
            "pathParameters": {
                "channelId": self.channel_id
            },
            "body": json.dumps({"signedAmount": 5})
        }

        response = update_consumed_balance(event = event, context = None)
        assert response["statusCode"] == 200

        channel = self.channel_repository.get_channel(self.channel_id)
        assert int(channel.consumed_balance) == 5

    @patch("contract_api.application.services.channel_service.ChannelService._get_channel_state_from_daemon")
    def test_update_consumed_balance_via_daemon(self, get_channel_state_from_daemon):
        get_channel_state_from_daemon.return_value = 5
        event = {
            "pathParameters": {
                "channelId": self.channel_id
            },
            "body": json.dumps({
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            })
        }

        response = update_consumed_balance(event = event, context = None)
        assert response["statusCode"] == 200

        channel = self.channel_repository.get_channel(self.channel_id)
        assert int(channel.consumed_balance) == 5
