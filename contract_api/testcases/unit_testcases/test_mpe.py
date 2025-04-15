from unittest import TestCase
from unittest.mock import patch

from common.repository import Repository
from contract_api.config import NETWORKS, NETWORK_ID
from contract_api.dao.mpe_repository import MPERepository
from contract_api.mpe import MPE


class TestMPE(TestCase):

    def setUp(self):
        self.NETWORKS_NAME = dict((NETWORKS[netId]["name"], netId) for netId in NETWORKS.keys())
        self.repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
        self.mpe = MPE(self.repo)

    @patch("contract_api.mpe.MPE._get_channel_state_from_daemon")
    def test_update_consumed_balance(self, mock_get_channel_state_from_daemon):
        mpe_repo = MPERepository(self.repo)
        mock_get_channel_state_from_daemon.return_value = 15
        mpe_repo.create_channel(
            {
                "channelId": 1,
                "sender": '0x123',
                "recipient": "0x345",
                "groupId": b"\xbc\xb0\xa1\x93Z\xa1\xab\x11\xfd\xbcX\x1c\x1cxZ\xdc.\xb6\xba\x8e\xc6\xc8C*\xd7\xa9\xea\x91\xe6'\xae\xfc",
                "amount": 100,
                "pending": 0,
                "nonce": 0,
                "expiration": 8396357,
                "signer": '0x987',
                "consumed_balance": 12
            }
        )
        mpe_repo.create_channel({
                "channelId": 2,
                "sender": '0x3432',
                "recipient": "0x5453",
                "groupId": b"\xbc\xb0\xa1\x93Z\xa1\xab\x11\xfd\xbcX\x1c\x1cxZ\xdc.\xb6\xba\x8e\xc6\xc8C*\xd7\xa9\xea\x91\xe6'\xae\xfc",
                "amount": 100,
                "pending": 0,
                "nonce": 1,
                "expiration": 8396357,
                "signer": '0x987',
                "consumed_balance": 3
            }
        )

        self.assertDictEqual({}, self.mpe.update_consumed_balance(1, signed_amount = 15))
        self.assertDictEqual({}, self.mpe.update_consumed_balance(2, org_id = "test_org", service_id = "test_service"))

        try:
            self.mpe.update_consumed_balance(3, signed_amount = 10)
        except Exception:
            assert True

    def tearDown(self):
        self.repo.execute(
            "DELETE FROM `mpe_channel`"
        )
