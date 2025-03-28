import base64
from datetime import datetime
from web3 import Web3
from cryptography.fernet import Fernet

from common.blockchain_util import BlockChainUtil
from common.boto_utils import BotoUtils
from common.constant import TransactionStatus
from common.logger import get_logger
from common.utils import Utils
from wallets.config import NETWORK_ID, NETWORKS, SIGNER_ADDRESS, EXECUTOR_ADDRESS, EXECUTOR_KEY, \
    MINIMUM_AMOUNT_IN_COGS_ALLOWED, REGION_NAME, ENCRYPTION_KEY
from wallets.constant import GENERAL_WALLET_TYPE, MPE_ADDR_PATH, MPE_CNTRCT_PATH, WalletStatus
from wallets.dao.channel_dao import ChannelDAO
from wallets.dao.wallet_data_access_object import WalletDAO
from wallets.domain.models.channel_transaction_history import ChannelTransactionHistoryModel
from wallets.infrastructure.repositories.channel_repository import ChannelRepository
from wallets.domain.models.wallet import WalletModel


channel_repo = ChannelRepository()
logger = get_logger(__name__)


class WalletService:
    def __init__(self, repo):
        self.repo = repo
        self.boto_utils = BotoUtils(region_name=REGION_NAME)
        self.blockchain_util = BlockChainUtil(
            provider_type="HTTP_PROVIDER",
            provider=NETWORKS[NETWORK_ID]['http_provider']
        )
        self.utils = Utils()
        self.channel_dao = ChannelDAO(repo=self.repo)
        self.wallet_dao = WalletDAO(repo=self.repo)
        self.ENCRYPTION_KEY = self.boto_utils.get_ssm_parameter(ENCRYPTION_KEY)
        self.fernet = Fernet(bytes.fromhex(self.ENCRYPTION_KEY))

    def create_and_register_wallet(self, username):
        address, private_key = self.blockchain_util.create_account()
        encrypted_key = self._encrypt_key(private_key)
        wallet = WalletModel(address=address, encrypted_key=encrypted_key,
                        type=GENERAL_WALLET_TYPE, status=WalletStatus.ACTIVE.value)
        self._register_wallet(wallet, username)
        wallet = wallet.to_response()
        wallet["private_key"] = private_key
        return wallet

    def _register_wallet(self, wallet, username):
        existing_wallet = self.wallet_dao.get_wallet_details(wallet)
        if len(existing_wallet) == 0:
            self.wallet_dao.insert_wallet(wallet)
        self.wallet_dao.add_user_for_wallet(wallet, username)

    def register_wallet(self, wallet_address, wallet_type, status, username):
        wallet = WalletModel(address=wallet_address, type=wallet_type, status=status)
        self._register_wallet(wallet, username)
        return wallet.to_response()

    def remove_user_wallet(self, username):
        self.wallet_dao.remove_user_wallet(username)

    def get_wallet_details(self, username):
        """ Method to get wallet details for a given username. """
        logger.info(f"Fetching wallet details for {username}")
        wallet_data = self.wallet_dao.get_wallet_data_by_username(username)
        self.utils.clean(wallet_data)

        wallets = []
        for wallet in wallet_data:
            new_wallet = wallet.to_response()
            if wallet.encrypted_key is not None:
                new_wallet['private_key'] = self._decrypt_key(wallet.encrypted_key)
            wallets.append(new_wallet)

        logger.info(f"Fetched {len(wallet_data)} wallets for username: {username}")
        wallet_response = {"username": username, "wallets": wallets}
        return wallet_response

    def __generate_signature_details(self, recipient, group_id, agi_tokens, expiration, message_nonce, signer_key):
        data_types = ["string", "address", "address", "address", "address", "bytes32", "uint256", "uint256",
                      "uint256"]
        values = ["__openChannelByThirdParty", self.mpe_address, self.EXECUTOR_WALLET_ADDRESS, SIGNER_ADDRESS,
                  recipient,
                  group_id, agi_tokens, expiration, message_nonce]
        signature = self.blockchain_util.generate_signature(data_types=data_types, values=values,
                                                            signer_key=signer_key)
        v, r, s = Web3.toInt(hexstr="0x" + signature[-2:]), signature[:66], "0x" + signature[66:130]
        return r, s, v, signature

    def __calculate_amount_in_cogs(self, amount, currency):
        if currency == "USD":
            amount_in_cogs = round(amount)
        else:
            raise Exception("Currency %s not supported.", currency)

        return amount_in_cogs

    def record_create_channel_event(self, payload):
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if not self.channel_dao.persist_create_channel_event(payload, current_time):
            raise Exception("Failed to create record")
        return {}

    def open_channel_by_third_party(self, order_id, sender, signature, r, s, v, group_id,
                                    org_id, amount, currency, recipient, current_block_no, amount_in_cogs):
        self.EXECUTOR_WALLET_ADDRESS = self.boto_utils.get_ssm_parameter(EXECUTOR_ADDRESS)
        self.EXECUTOR_WALLET_KEY = self.boto_utils.get_ssm_parameter(EXECUTOR_KEY)
        method_name = "openChannelByThirdParty"
        self.mpe_address = self.blockchain_util.read_contract_address(
            net_id=NETWORK_ID, path=MPE_ADDR_PATH,
            key='address'
        )

        # 1 block no is mined in 15 sec on average, setting expiration as 10 years
        expiration = current_block_no + (10 * 365 * 24 * 60 * 4)
        # amount_in_cogs = self.__calculate_amount_in_cogs(amount=amount, currency=currency)
        self.__validate__cogs(amount_in_cogs=amount_in_cogs)

        group_id_in_hex = "0x" + base64.b64decode(group_id).hex()

        positional_inputs = (
            sender, SIGNER_ADDRESS, recipient,
            group_id_in_hex, amount_in_cogs, expiration,
            current_block_no, v, r, s
        )

        transaction_object = self.blockchain_util.create_transaction_object(
            *positional_inputs,
            method_name=method_name,
            address=self.EXECUTOR_WALLET_ADDRESS,
            contract_path=MPE_CNTRCT_PATH,
            contract_address_path=MPE_ADDR_PATH,
            net_id=NETWORK_ID,
            gas=250000
        )

        raw_transaction = self.blockchain_util.sign_transaction_with_private_key(
            transaction_object=transaction_object,
            private_key=self.EXECUTOR_WALLET_KEY)
        transaction_hash = self.blockchain_util.process_raw_transaction(raw_transaction=raw_transaction)

        logger.info("openChannelByThirdParty::transaction_hash : %s for order_id : %s", transaction_hash, order_id)

        channel_repo.update_channel_transaction_history_status_by_order_id(
            channel_txn_history=ChannelTransactionHistoryModel(
                order_id=order_id, amount=amount, currency=currency,
                group_id=group_id, org_id=org_id,
                type=method_name, recipient=recipient,
                address=sender, signature=signature,
                request_parameters=str(positional_inputs),
                transaction_hash=transaction_hash,
                status=TransactionStatus.PENDING
            )
        )

        return {
            "transaction_hash": transaction_hash, "signature": signature,
            "amount_in_cogs": amount_in_cogs, "type": method_name
        }

    def set_default_wallet(self, username, address):
        self.wallet_dao.set_default_wallet(username=username, address=address)
        return "OK"

    def add_funds_to_channel(self, org_id, group_id, channel_id, sender, recipient, order_id, amount, currency, amount_in_cogs):
        self.EXECUTOR_WALLET_ADDRESS = self.boto_utils.get_ssm_parameter(EXECUTOR_ADDRESS)
        self.EXECUTOR_WALLET_KEY = self.boto_utils.get_ssm_parameter(EXECUTOR_KEY)
        method_name = "channelAddFunds"
        # amount_in_cogs = self.__calculate_amount_in_cogs(amount=amount, currency=currency)
        self.__validate__cogs(amount_in_cogs=amount_in_cogs)
        positional_inputs = (channel_id, amount_in_cogs)

        transaction_object = self.blockchain_util.create_transaction_object(
            *positional_inputs, method_name=method_name,
            address=self.EXECUTOR_WALLET_ADDRESS,
            contract_path=MPE_CNTRCT_PATH,
            contract_address_path=MPE_ADDR_PATH,
            net_id=NETWORK_ID
        )

        raw_transaction = self.blockchain_util.sign_transaction_with_private_key(
            transaction_object=transaction_object,
            private_key=self.EXECUTOR_WALLET_KEY)

        transaction_hash = self.blockchain_util.process_raw_transaction(raw_transaction=raw_transaction)
        logger.info("channelAddFunds::transaction_hash: %s for order_id: %s", transaction_hash, order_id)

        channel_repo.update_channel_transaction_history_status_by_order_id(
            channel_txn_history=ChannelTransactionHistoryModel(
                order_id=order_id, amount=amount, currency=currency,
                group_id=group_id, org_id=org_id,
                type=method_name, recipient=recipient,
                address=sender, signature=None,
                request_parameters=str(positional_inputs),
                transaction_hash=transaction_hash,
                status=TransactionStatus.PENDING
            )
        )
        return {"transaction_hash": transaction_hash, "amount_in_cogs": amount_in_cogs, "type": method_name}

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

    def __validate__cogs(self, amount_in_cogs):
        if amount_in_cogs < MINIMUM_AMOUNT_IN_COGS_ALLOWED:
            raise Exception("Insufficient amount to buy minimum amount in cogs allowed.")

    def _encrypt_key(self, private_key: str) -> str:
        key_in_bytes = bytes.fromhex(private_key)
        encrypted_key = self.fernet.encrypt(key_in_bytes)
        return encrypted_key.hex()

    def _decrypt_key(self, encrypted_key: str) -> str:
        encrypted_key_in_bytes = bytes.fromhex(encrypted_key)
        decrypted_key = self.fernet.decrypt(encrypted_key_in_bytes)
        return decrypted_key.hex()


