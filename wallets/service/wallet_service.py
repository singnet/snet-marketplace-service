import base64

from web3 import Web3
from common.blockchain_util import BlockChainUtil
from common.constant import TransactionStatus
from common.logger import get_logger
from common.ssm_utils import get_ssm_parameter
from common.utils import Utils
from wallets.config import NETWORK_ID, NETWORKS, SIGNER_ADDRESS, EXECUTOR_ADDRESS, EXECUTOR_KEY
from wallets.constant import GENERAL_WALLET_TYPE, MPE_ADDR_PATH, MPE_CNTRCT_PATH
from wallets.dao.channel_dao import ChannelDAO
from wallets.dao.wallet_data_access_object import WalletDAO
from wallets.wallet import Wallet

logger = get_logger(__name__)


class WalletService:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_blockchain_util = BlockChainUtil(
            provider_type="HTTP_PROVIDER",
            provider=NETWORKS[NETWORK_ID]['http_provider']
        )
        self.utils = Utils()
        self.channel_dao = ChannelDAO(obj_repo=self.repo)
        self.obj_wallet_dao = WalletDAO(obj_repo=self.repo)

    def create_and_register_wallet(self, username):
        address, private_key = self.obj_blockchain_util.create_account()
        obj_wallet = Wallet(address=address, private_key=private_key, type=GENERAL_WALLET_TYPE, status=0)
        registered = self.register_wallet(username=username, obj_wallet=obj_wallet)
        if registered:
            return obj_wallet.get_wallet()
        raise Exception("Unable to create and register wallet.")

    def register_wallet(self, username, obj_wallet):
        wallet_details = obj_wallet.get_wallet()

        persisted = self.obj_wallet_dao.insert_wallet_details(
            username=username,
            address=wallet_details["address"],
            type=wallet_details["type"],
            status=wallet_details["status"]
        )

        if persisted:
            return True
        raise Exception("Unable to register wallet.")

    def get_wallet_details(self, username):
        """ Method to get wallet details for a given username. """
        logger.info(f"Fetching wallet details for {username}")
        wallet_data = self.obj_wallet_dao.get_wallet_data_by_username(username)
        self.utils.clean(wallet_data)

        logger.info(f"Fetched {len(wallet_data)} wallets for username: {username}")
        wallet_response = {"username": username, "wallets": wallet_data}
        return wallet_response

    def __generate_signature_details(self, recipient, group_id, agi_tokens, expiration, message_nonce, signer_key):
        data_types = ["string", "address", "address", "address", "address", "bytes32", "uint256", "uint256",
                      "uint256"]
        values = ["__openChannelByThirdParty", self.mpe_address, self.EXECUTOR_WALLET_ADDRESS, SIGNER_ADDRESS,
                  recipient,
                  group_id, agi_tokens, expiration, message_nonce]
        signature = self.obj_blockchain_util.generate_signature(data_types=data_types, values=values,
                                                                signer_key=signer_key)
        v, r, s = Web3.toInt(hexstr="0x" + signature[-2:]), signature[:66], "0x" + signature[66:130]
        return r, s, v, signature

    def __calculate_agi_tokens(self, amount, currency):
        if currency == "USD":
            agi_tokens = amount
        else:
            raise Exception("Currency %s not supported.", currency)

        return agi_tokens

    def open_channel_by_third_party(self, order_id, sender, sender_private_key, group_id,
                                    org_id, amount, currency, recipient):
        self.EXECUTOR_WALLET_ADDRESS = get_ssm_parameter(EXECUTOR_ADDRESS)
        self.EXECUTOR_WALLET_KEY = get_ssm_parameter(EXECUTOR_KEY)
        method_name = "openChannelByThirdParty"
        self.mpe_address = self.obj_blockchain_util.read_contract_address(
            net_id=NETWORK_ID, path=MPE_ADDR_PATH,
            key='address'
        )

        current_block_no = self.obj_blockchain_util.get_current_block_no()

        # 1 block no is mined in 15 sec on average, setting expiration as 10 years
        expiration = current_block_no + (10 * 365 * 24 * 60 * 4)
        agi_tokens = self.__calculate_agi_tokens(amount=amount, currency=currency)

        group_id_in_hex = "0x" + base64.b64decode(group_id).hex()
        r, s, v, signature = self.__generate_signature_details(
            recipient=recipient, group_id=group_id_in_hex,
            agi_tokens=agi_tokens, expiration=expiration,
            message_nonce=current_block_no,
            signer_key=sender_private_key
        )

        positional_inputs = (
            sender, SIGNER_ADDRESS, recipient,
            group_id_in_hex, agi_tokens, expiration,
            current_block_no, v, r, s
        )

        transaction_object = self.obj_blockchain_util.create_transaction_object(
            *positional_inputs,
            method_name=method_name,
            address=self.EXECUTOR_WALLET_ADDRESS,
            contract_path=MPE_CNTRCT_PATH,
            contract_address_path=MPE_ADDR_PATH,
            net_id=NETWORK_ID
        )

        raw_transaction = self.obj_blockchain_util.sign_transaction_with_private_key(
            transaction_object=transaction_object,
            private_key=self.EXECUTOR_WALLET_KEY)
        transaction_hash = self.obj_blockchain_util.process_raw_transaction(raw_transaction=raw_transaction)

        logger.info("openChannelByThirdParty::transaction_hash", transaction_hash)

        self.channel_dao.insert_channel_history(
            order_id=order_id, amount=amount, currency=currency,
            group_id=group_id, org_id=org_id,
            type=method_name, recipient=recipient,
            address=sender, signature=signature,
            request_parameters=str(positional_inputs),
            transaction_hash=transaction_hash, status=TransactionStatus.PENDING
        )

        return {
            "transaction_hash": transaction_hash, "signature": signature,
            "agi_tokens": agi_tokens, "type": method_name
        }

    def set_default_wallet(self, username, address):
        self.obj_wallet_dao.set_default_wallet(username=username, address=address)
        return "OK"

    def add_funds_to_channel(self, org_id, group_id, channel_id, sender, recipient, order_id, amount, currency):
        self.EXECUTOR_WALLET_ADDRESS = get_ssm_parameter(EXECUTOR_ADDRESS)
        self.EXECUTOR_WALLET_KEY = get_ssm_parameter(EXECUTOR_KEY)
        method_name = "channelAddFunds"
        agi_tokens = self.__calculate_agi_tokens(amount=amount, currency=currency)
        positional_inputs = (channel_id, agi_tokens)

        transaction_object = self.obj_blockchain_util.create_transaction_object(
            *positional_inputs, method_name=method_name,
            address=self.EXECUTOR_WALLET_ADDRESS,
            contract_path=MPE_CNTRCT_PATH,
            contract_address_path=MPE_ADDR_PATH,
            net_id=NETWORK_ID
        )

        raw_transaction = self.obj_blockchain_util.sign_transaction_with_private_key(
            transaction_object=transaction_object,
            private_key=self.EXECUTOR_WALLET_KEY)

        transaction_hash = self.obj_blockchain_util.process_raw_transaction(raw_transaction=raw_transaction)
        logger.info("channelAddFunds::transaction_hash", transaction_hash)

        self.channel_dao.insert_channel_history(
            order_id=order_id, amount=amount, currency=currency,
            group_id=group_id, org_id=org_id,
            type=method_name, recipient=recipient,
            address=sender, signature=None,
            request_parameters=str(positional_inputs),
            transaction_hash=transaction_hash, status=TransactionStatus.PENDING
        )
        return {"transaction_hash": transaction_hash, "agi_tokens": agi_tokens, "type": method_name}

    def get_transactions_from_username_recipient(self, username, org_id, group_id):
        logger.info(f"Fetching transactions for {username} to org_id: {org_id} group_id: {org_id}")
        channel_data = self.channel_dao.get_channel_transactions_for_username_recipient(
            username=username, group_id=group_id, org_id=org_id)
        self.utils.clean(channel_data)

        logger.info(f"Fetched {len(channel_data)} transactions")
        transaction_details = {
            "username": username,
            "wallets": []
        }

        wallet_transactions = dict()
        for rec in channel_data:
            sender_address = rec["address"]
            if rec["address"] not in wallet_transactions:
                wallet_transactions[rec["address"]] = {
                    "address": sender_address,
                    "is_default": rec["is_default"],
                    "type": rec["type"],
                    "transactions": []
                }
            if rec['recipient'] is None:
                continue

            transaction = {
                "org_id": org_id,
                "group_id": group_id,
                "recipient": rec["recipient"],
                "amount": rec["amount"],
                "transaction_type": rec["transaction_type"],
                "currency": rec["currency"],
                "status": rec["status"],
                "created_at": rec["created_at"],
            }

            wallet_transactions[sender_address]["transactions"].append(transaction)

        for key in wallet_transactions:
            wallet = wallet_transactions[key]
            transaction_details["wallets"].append(wallet)
        return transaction_details

    def get_channel_transactions_against_order_id(self, order_id):
        transaction_history = self.channel_dao.get_channel_transactions_against_order_id(order_id)

        for record in transaction_history:
            record["created_at"] = record["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return {
            "order_id": order_id,
            "transactions": transaction_history
        }
