import base64
import unittest

from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.config import EXECUTOR_ADDRESS, EXECUTOR_KEY, SIGNER_ADDRESS, NETWORKS, SIGNER_KEY
from common.constant import MPE_CNTRCT_PATH, MPE_ADDR_PATH


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.net_id = 11155111
        self.http_provider = Web3.HTTPProvider(NETWORKS[self.net_id]['http_provider'])
        self.obj_utils = BlockChainUtil(provider_type="HTTP_PROVIDER", provider=self.http_provider)
        self.mpe_address = self.obj_utils.read_contract_address(net_id=self.net_id, path=MPE_ADDR_PATH, key='address')
        self.recipient = "0x9c302750c50307D3Ad88eaA9a6506874a15cE4Cb"
        self.group_id = "0x" + base64.b64decode("DS2OoKSfGE/7hAO/023psl4Qdj0MJvYsreJbCoAHVSc=").hex()
        self.agi_tokens = 1
        self.current_block_no = self.obj_utils.get_current_block_no()
        self.expiration = self.current_block_no + 10000000
        self.channel_id = 0

    def generate_signature(self, message_nonce, signer_key):
        data_types = ["string", "address", "address", "address", "address", "bytes32", "uint256", "uint256", "uint256"]
        values = ["__openChannelByThirdParty", self.mpe_address, EXECUTOR_ADDRESS, SIGNER_ADDRESS, self.recipient,
                  self.group_id, self.agi_tokens, self.expiration, message_nonce]
        signature = self.obj_utils.generate_signature(data_types=data_types, values=values, signer_key=signer_key)
        v, r, s = Web3.toInt(hexstr="0x" + signature[-2:]), signature[:66], "0x" + signature[66:130]
        assert(v == 27 or v == 28)
        assert(len(r) == 66)
        assert(len(s) == 66)
        assert(len(signature) == 132)
        return r, s, v, signature

    def test_create_account(self):
        address, private_key = self.obj_utils.create_account()
        assert (Web3.isAddress(address) is True)
        return address, private_key

    def test_create_transaction_object1(self):
        method_name = "openChannelByThirdParty"
        sender, sender_private_key = self.test_create_account()
        message_nonce = self.obj_utils.get_current_block_no()
        r, s, v, _ = self.generate_signature(message_nonce=message_nonce, signer_key=sender_private_key)
        positional_inputs = (sender, SIGNER_ADDRESS, self.recipient, self.group_id, self.agi_tokens, self.expiration, message_nonce, v, r, s)
        transaction_object = self.obj_utils.create_transaction_object(*positional_inputs, method_name=method_name,
                                                                      address=EXECUTOR_ADDRESS,
                                                                      contract_path=MPE_CNTRCT_PATH,
                                                                      contract_address_path=MPE_ADDR_PATH,
                                                                      net_id=self.net_id)
        print(transaction_object)
        raw_transaction = self.obj_utils.sign_transaction_with_private_key(transaction_object=transaction_object,
                                                                           private_key=EXECUTOR_KEY)
        transaction_hash = self.obj_utils.process_raw_transaction(raw_transaction=raw_transaction)
        print("openChannelByThirdParty::transaction_hash", transaction_hash)

    def test_create_transaction_object2(self):
        method_name = "channelAddFunds"
        positional_inputs = (self.channel_id, self.agi_tokens)
        transaction_object = self.obj_utils.create_transaction_object(*positional_inputs, method_name=method_name,
                                                                      address=EXECUTOR_ADDRESS,
                                                                      contract_path=MPE_CNTRCT_PATH,
                                                                      contract_address_path=MPE_ADDR_PATH,
                                                                      net_id=self.net_id)
        print(transaction_object)
        raw_transaction = self.obj_utils.sign_transaction_with_private_key(transaction_object=transaction_object,
                                                                           private_key=EXECUTOR_KEY)

        transaction_hash = self.obj_utils.process_raw_transaction(raw_transaction=raw_transaction)
        print("channelAddFunds::transaction_hash", transaction_hash)

    def test_generate_signature_for_state_service(self):
        channel_id = 1
        data_types = ["string", "address", "uint256", "uint256"]
        self.current_block_no = 6487832
        values = ["__get_channel_state", self.mpe_address, channel_id, self.current_block_no]
        signature = self.obj_utils.generate_signature(data_types=data_types, values=values, signer_key=SIGNER_KEY)
        _, _, _ = Web3.toInt(hexstr="0x" + signature[-2:]), signature[:66], "0x" + signature[66:130]
        assert(signature == "0x0b9bb258a0f975328fd9cd9608bd9b570e7b68cad8d337c940e32b9413e348437dd3614f9c6f776b1eb62d521a5794204a010f581721f167c5b26de0928b139d1c")

    def test_generate_signature_for_daemon_call(self):
        channel_id = 1
        amount = 10
        nonce = 1
        data_types = ["string", "address", "uint256", "uint256", "uint256"]
        values = ["__MPE_claim_message", self.mpe_address, channel_id, nonce, amount]
        signature = self.obj_utils.generate_signature(data_types=data_types, values=values, signer_key=SIGNER_KEY)
        _, _, _ = Web3.toInt(hexstr="0x" + signature[-2:]), signature[:66], "0x" + signature[66:130]
        assert(signature == "0x7e50ac20909da29f72ed2ab9cf6c6375f853d8eddfcf3ce33806a4e27b30bcbd5366c41a59647467f0519b0bfc89a50d890b683cd797d5566ba03937f82819c41b")
