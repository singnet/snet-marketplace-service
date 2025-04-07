import datetime as dt
import base64
import json

from common.logger import get_logger
from common.utils import Utils
# from common.blockchain_util import BlockChainUtil
from wallets.infrastructure.blockchain_util import BlockChainUtil
"""
Temporarily moved for latest web3 version for python 3.12
TODO: change back when 'common' is updated
"""
from common.boto_utils import BotoUtils
from common.constant import TransactionStatus

from wallets.config import NETWORK_ID, NETWORKS, SIGNER_ADDRESS, EXECUTOR_ADDRESS, EXECUTOR_KEY, \
    MINIMUM_AMOUNT_IN_COGS_ALLOWED, REGION_NAME, GET_RAW_EVENT_DETAILS
from wallets.infrastructure.repositories.channel_repository import ChannelRepository
from wallets.constant import MPE_ADDR_PATH, MPE_CNTRCT_PATH
from wallets.domain.models.channel_transaction_history import ChannelTransactionHistoryModel


logger = get_logger(__name__)


class ChannelService:
    def __init__(self):
        self.boto_utils = BotoUtils(region_name = REGION_NAME)
        self.blockchain_util = BlockChainUtil(
            provider_type = "HTTP_PROVIDER",
            provider = NETWORKS[NETWORK_ID]['http_provider']
        )
        self.utils = Utils()
        self.channel_repo = ChannelRepository()

    def add_funds_to_channel(self, org_id, group_id, channel_id, sender, recipient, order_id, amount, currency, amount_in_cogs): # ------------------------------
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

        self.channel_repo.update_channel_transaction_history_status_by_order_id(
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
        channel_data = self.channel_repo.get_channel_transactions_for_username_recipient(
            username=username, group_id=group_id, org_id=org_id)

        logger.info(f"Fetched {len(channel_data)} transactions")
        transaction_details = {
            "username": username,
            "wallets": []
        }

        transactions = []
        for rec in channel_data:
            if rec[2] is not None:
                transaction = rec[2].to_dict()
                transaction["transaction_type"] = transaction["type"]
                del transaction["type"]
            else:
                transaction = {}
            user_wallet = rec[0].to_dict()
            user_wallet["type"] = rec[1].type
            transaction.update(user_wallet)
            transaction["has_private_key"] = int(rec[1].encrypted_key is not None and rec[1].encrypted_key != "")
            transactions.append(transaction)

        wallet_transactions = {}
        for rec in transactions:
            sender_address = rec["address"]
            if rec["address"] not in wallet_transactions:
                wallet_transactions[sender_address] = {
                    "address": sender_address,
                    "is_default": int(rec["is_default"]),
                    "type": rec["type"],
                    "has_private_key": rec["has_private_key"],
                    "transactions": []
                }
            if 'recipient' not in rec:
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
        transaction_history = self.channel_repo.get_channel_transactions_against_order_id(order_id)
        logger.info(f"Fetched {len(transaction_history)} transactions against order_id: {order_id}")

        transactions = []
        for transaction in transaction_history:
            transactions.append(transaction.to_dict())

        return {
            "order_id": order_id,
            "transactions": transactions
        }

    def record_create_channel_event(self, payload):
        self.channel_repo.add_channel_transaction_history_record(ChannelTransactionHistoryModel(
            order_id = payload["order_id"],
            amount = payload["amount"],
            currency = payload["currency"],
            type = payload.get("type", "openChannelByThirdParty"),
            address = payload["sender"],
            recipient = payload["recipient"],
            signature = payload["signature"],
            org_id = payload["org_id"],
            group_id = payload["group_id"],
            request_parameters = payload.get("request_parameters", ""),
            transaction_hash = payload.get("transaction_hash", ""),
            status = TransactionStatus.NOT_SUBMITTED
        ))

        current_time = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M:%S")
        if not self.channel_repo.persist_create_channel_event(payload, current_time):
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

        self.channel_repo.update_channel_transaction_history_status_by_order_id(
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

    @staticmethod
    def __validate__cogs(amount_in_cogs):
        if amount_in_cogs < MINIMUM_AMOUNT_IN_COGS_ALLOWED:
            raise Exception("Insufficient amount to buy minimum amount in cogs allowed.")

    def get_mpe_processed_transactions_from_event_pub_sub(self, transaction_list):
        response = self.boto_utils.invoke_lambda(
            payload=json.dumps({"transaction_hash_list": transaction_list, "contract_name": "MPE"}),
            lambda_function_arn=GET_RAW_EVENT_DETAILS,
            invocation_type="RequestResponse"
        )
        if response["statusCode"] != 200:
            raise Exception("Error getting processed transactions from event pubsub")
        return json.loads(response["body"])["data"]

    def manage_channel_transaction_status(self):
        # UPDATE PENDING TRANSACTIONS
        pending_txns_db = self.channel_repo.get_channel_transaction_history_data(status=TransactionStatus.PENDING)
        for txn_data in pending_txns_db:
            if txn_data.transaction_hash:
                txn_receipt = self.blockchain_util.get_transaction_receipt_from_blockchain(
                    transaction_hash=txn_data.transaction_hash)
                if txn_receipt:
                    txn_data.status = TransactionStatus.PROCESSING if txn_receipt.status == 1 else TransactionStatus.FAILED
                    self.channel_repo.update_channel_transaction_history_status_by_order_id(channel_txn_history=txn_data)

        # UPDATE PROCESSING TRANSACTIONS
        processing_txns_db = self.channel_repo.get_channel_transaction_history_data(status=TransactionStatus.PROCESSING)
        processing_txn = [txn.transaction_hash for txn in processing_txns_db]
        if processing_txns_db:
            processed_transactions = self.get_mpe_processed_transactions_from_event_pub_sub(processing_txn)
            for txn in processed_transactions:
                if txn["processed"]:
                    txn_data = list(filter(lambda x: x.transaction_hash == txn["transactionHash"], processing_txns_db))[0]
                    txn_data.status = TransactionStatus.SUCCESS
                    self.channel_repo.update_channel_transaction_history_status_by_order_id(channel_txn_history=txn_data)

    def manage_create_channel_event(self):
        pending_create_channel_event = self.channel_repo.get_one_create_channel_event(TransactionStatus.PENDING)
        if pending_create_channel_event is None:
            logger.info("No create channel event with status PENDING")
            return
        payload = json.loads(pending_create_channel_event.payload)
        logger.info(f"Payload for create channel: {payload}")
        try:
            self.open_channel_by_third_party(
                order_id = payload['order_id'], sender = payload['sender'], signature = payload['signature'],
                r = payload['r'], s = payload['s'], v = payload['v'], current_block_no = payload['current_block_no'],
                group_id = payload['group_id'], org_id = payload["org_id"], recipient = payload['recipient'],
                amount = payload['amount'], currency = payload['currency'],
                amount_in_cogs = payload['amount_in_cogs']
            )
            self.channel_repo.update_create_channel_event(pending_create_channel_event, TransactionStatus.SUCCESS)
            logger.info("Channel successfully created")
        except Exception as e:
            self.channel_repo.update_create_channel_event(pending_create_channel_event, TransactionStatus.FAILED)
            logger.info(f"Channel creation failed: {str(e)}")
