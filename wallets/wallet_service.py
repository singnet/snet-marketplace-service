from web3 import Web3
import base64
from common.blockchain_util import BlockChainUtil
from common.ssm_utils import get_ssm_parameter
from wallets.config import (
    NETWORK_ID,
    NETWORKS,
    SIGNER_ADDRESS,
    EXECUTOR_ADDRESS,
    EXECUTOR_KEY,
)
from wallets.constant import GENERAL_WALLET_TYPE, MPE_ADDR_PATH, MPE_CNTRCT_PATH
from wallets.wallet import Wallet
from wallets.wallet_data_access_object import WalletDAO

EXECUTOR_WALLET_ADDRESS = get_ssm_parameter(EXECUTOR_ADDRESS)
EXECUTOR_WALLET_KEY = get_ssm_parameter(EXECUTOR_KEY)


class WalletService:
    def __init__(self, obj_repo):
        self.obj_repo = obj_repo

    def create_and_register_wallet(self):
        self.obj_blockchain_util = BlockChainUtil(
            provider_type="HTTP_PROVIDER",
            provider=NETWORKS[NETWORK_ID]["http_provider"],
        )
        address, private_key = self.obj_blockchain_util.create_account()
        obj_wallet = Wallet(
            address=address, private_key=private_key, type=GENERAL_WALLET_TYPE, status=0
        )
        registered = self.register_wallet(obj_wallet=obj_wallet)
        if registered:
            return obj_wallet.get_wallet()
        raise Exception("Unable to create and register wallet.")

    def register_wallet(self, obj_wallet):
        wallet_details = obj_wallet.get_wallet()
        obj_wallet_dao = WalletDAO(obj_repo=self.obj_repo)
        persisted = obj_wallet_dao.insert_wallet_details(
            address=wallet_details["address"],
            type=wallet_details["type"],
            status=wallet_details["status"],
        )
        if persisted:
            return True
        raise Exception("Unable to register wallet.")

    def __generate_signature_details(
        self, recipient, group_id, agi_tokens, expiration, message_nonce, signer_key
    ):
        data_types = [
            "string",
            "address",
            "address",
            "address",
            "address",
            "bytes32",
            "uint256",
            "uint256",
            "uint256",
        ]
        values = [
            "__openChannelByThirdParty",
            self.mpe_address,
            EXECUTOR_WALLET_ADDRESS,
            SIGNER_ADDRESS,
            recipient,
            group_id,
            agi_tokens,
            expiration,
            message_nonce,
        ]
        signature = self.obj_blockchain_util.generate_signature(
            data_types=data_types, values=values, signer_key=signer_key
        )
        v, r, s = (
            Web3.toInt(hexstr="0x" + signature[-2:]),
            signature[:66],
            "0x" + signature[66:130],
        )
        return r, s, v, signature

    def __calculate_agi_tokens(self, amount, currency):
        if currency == "USD":
            agi_tokens = amount
        else:
            raise Exception("Currency %s not supported.", currency)

        return agi_tokens

    def open_channel_by_third_party(
        self,
        order_id,
        sender,
        sender_private_key,
        group_id,
        amount,
        currency,
        recipient,
    ):
        obj_wallet_dao = WalletDAO(obj_repo=self.obj_repo)
        self.obj_blockchain_util = BlockChainUtil(
            provider_type="HTTP_PROVIDER",
            provider=NETWORKS[NETWORK_ID]["http_provider"],
        )
        method_name = "openChannelByThirdParty"
        self.mpe_address = self.obj_blockchain_util.read_contract_address(
            net_id=NETWORK_ID, path=MPE_ADDR_PATH, key="address"
        )
        current_block_no = self.obj_blockchain_util.get_current_block_no()
        # 1 block no is mined in 15 sec on average, setting expiration as 10 years
        expiration = current_block_no + (10 * 365 * 24 * 60 * 4)
        agi_tokens = self.__calculate_agi_tokens(amount=amount, currency=currency)
        group_id_in_hex = "0x" + base64.b64decode(group_id).hex()
        r, s, v, signature = self.__generate_signature_details(
            recipient=recipient,
            group_id=group_id_in_hex,
            agi_tokens=agi_tokens,
            expiration=expiration,
            message_nonce=current_block_no,
            signer_key=sender_private_key,
        )
        positional_inputs = (
            sender,
            SIGNER_ADDRESS,
            recipient,
            group_id_in_hex,
            agi_tokens,
            expiration,
            current_block_no,
            v,
            r,
            s,
        )
        transaction_object = self.obj_blockchain_util.create_transaction_object(
            *positional_inputs,
            method_name=method_name,
            address=EXECUTOR_WALLET_ADDRESS,
            contract_path=MPE_CNTRCT_PATH,
            contract_address_path=MPE_ADDR_PATH,
            net_id=NETWORK_ID
        )
        raw_transaction = self.obj_blockchain_util.sign_transaction_with_private_key(
            transaction_object=transaction_object, private_key=EXECUTOR_WALLET_KEY
        )
        transaction_hash = self.obj_blockchain_util.process_raw_transaction(
            raw_transaction=raw_transaction
        )
        print("openChannelByThirdParty::transaction_hash", transaction_hash)
        obj_wallet_dao.insert_channel_history(
            order_id=order_id,
            amount=amount,
            currency=currency,
            type=method_name,
            address=sender,
            signature=signature,
            request_parameters=str(positional_inputs),
            transaction_hash=transaction_hash,
            status=0,
        )

        return {
            "transaction_hash": transaction_hash,
            "signature": signature,
            "agi_tokens": agi_tokens,
            "positional_inputs": positional_inputs,
            "type": method_name,
        }

    def update_wallet_status(self, address):
        pass

    def add_funds_to_channel(self, order_id, channel_id, amount, currency):
        method_name = "channelAddFunds"
        agi_tokens = self.__calculate_agi_tokens(amount=amount, currency=currency)
        positional_inputs = (channel_id, agi_tokens)
        transaction_object = self.obj_utils.create_transaction_object(
            *positional_inputs,
            method_name=method_name,
            address=EXECUTOR_WALLET_ADDRESS,
            contract_path=MPE_CNTRCT_PATH,
            contract_address_path=MPE_ADDR_PATH,
            net_id=self.net_id
        )
        raw_transaction = self.obj_utils.sign_transaction_with_private_key(
            transaction_object=transaction_object, private_key=EXECUTOR_WALLET_KEY
        )

        transaction_hash = self.obj_utils.process_raw_transaction(
            raw_transaction=raw_transaction
        )
        print("channelAddFunds::transaction_hash", transaction_hash)
        return {
            "transaction_hash": transaction_hash,
            "agi_tokens": agi_tokens,
            "positional_inputs": positional_inputs,
            "type": method_name,
        }
