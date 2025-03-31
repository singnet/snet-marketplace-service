import json

from common.blockchain_util import BlockChainUtil
from common.boto_utils import BotoUtils
from common.constant import TransactionStatus
from common.logger import get_logger
from wallets.config import NETWORKS, NETWORK_ID, REGION_NAME, GET_RAW_EVENT_DETAILS
from wallets.infrastructure.repositories.channel_repository import ChannelRepository


logger = get_logger(__name__)


class ChannelTransactionStatusService:
    def __init__(self):
        self.boto_utils = BotoUtils(region_name = REGION_NAME)
        self.channel_repo = ChannelRepository()
        self.obj_blockchain_util = BlockChainUtil(provider_type = "HTTP_PROVIDER",
                                             provider = NETWORKS[NETWORK_ID]['http_provider'])

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
                txn_receipt = self.obj_blockchain_util.get_transaction_receipt_from_blockchain(
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
