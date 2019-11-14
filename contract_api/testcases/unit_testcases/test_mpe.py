from unittest import TestCase
from unittest.mock import patch

from common.repository import Repository
from contract_api.config import NETWORKS, NETWORK_ID
from contract_api.mpe import MPE


class TestMPE(TestCase):

    def setUp(self):
        self.NETWORKS_NAME = dict((NETWORKS[netId]["name"], netId) for netId in NETWORKS.keys())
        self.repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
        self.mpe = MPE(self.repo)

    def test_update_consumed_balance(self):
        self.repo.execute(
            "INSERT INTO `mpe_channel` "
            "(channel_id, sender, recipient, groupId, balance_in_cogs, pending, nonce, "
            "expiration, signer, consumed_balance) "
            "VALUES (1, '0x123', '0x345', 'group-123', 100, 0, 0, 8396357, '0x987', 12),"
            "(2, '0x3432', '0x5453', 'group-123', 100, 0, 1, 8396357, '0x987', 3);"
        )

        self.assertDictEqual({}, self.mpe.update_consumed_balance(1, 13, 100, 0))
        try:
            self.mpe.update_consumed_balance(2, 2, 100, 1)
        except:
            assert True

        try:
            self.mpe.update_consumed_balance(2, 4, 100, 0)
        except:
            assert True
        try:
            self.mpe.update_consumed_balance(2, 4, 80, 1)
        except:
            assert True

    def tearDown(self):
        self.repo.execute(
            "DELETE FROM `mpe_channel`"
        )
