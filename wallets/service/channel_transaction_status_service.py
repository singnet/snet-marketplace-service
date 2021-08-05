import json

from common.blockchain_util import BlockChainUtil
from common.constant import TransactionStatus
from common.logger import get_logger
from wallets.dao.channel_transaction_status_data_access_object import \
    ChannelTransactionStatusDataAccessObject
from wallets.config import NETWORKS, NETWORK_ID, REGION_NAME, GET_MPE_PROCESSED_TRANSACTION_ARN
from common.boto_utils import BotoUtils
from wallets.infrastructure.repositories.channel_repository import ChannelRepository

boto_utils = BotoUtils(region_name=REGION_NAME)
channel_repo = ChannelRepository()
logger = get_logger(__name__)
obj_blockchain_util = BlockChainUtil(provider_type="HTTP_PROVIDER",
                                     provider=NETWORKS[NETWORK_ID]['http_provider'])


class ChannelTransactionStatusService:
    def __init__(self):
        pass

    @staticmethod
    def get_mpe_processed_transactions_from_event_pub_sub(transaction_list):
        response = boto_utils.invoke_lambda(
            payload=json.dumps({"transaction_hash_list": transaction_list, "contract_name": "MPE"}),
            lambda_function_arn=GET_MPE_PROCESSED_TRANSACTION_ARN,
            invocation_type="RequestResponse"
        )
        if response["statusCode"] != 200:
            raise Exception("Error getting processed transactions from event pubsub")
        return json.loads(response["body"])["data"]

    def manage_channel_transaction_status(self):
        # UPDATE PENDING TRANSACTIONS
        pending_txns_db = channel_repo.get_channel_transaction_history_data(status=TransactionStatus.PENDING)
        logger.info(f"Pending transactions :: {[txn for txn in pending_txns_db]}")
        for txn_data in pending_txns_db:
            if txn_data.transaction_hash:
                txn_receipt = obj_blockchain_util.get_transaction_receipt_from_blockchain(
                    transaction_hash=txn_data.transaction_hash)
                txn_data.status = TransactionStatus.PROCESSING if txn_receipt.status == 1 else TransactionStatus.FAILED
            else:
                txn_data.status = TransactionStatus.NOT_SUBMITTED
            channel_repo.update_channel_transaction_history_status(channel_txn_history=txn_data)

        # UPDATE PROCESSING TRANSACTIONS
        processing_txns_db = channel_repo.get_channel_transaction_history_data(status=TransactionStatus.PROCESSING)
        logger.info(f"Processing transactions :: {[txn.transaction_hash for txn in processing_txns_db]}")
        processing_txn = [txn.transaction_hash for txn in processing_txns_db]
        if processing_txns_db:
            processed_transactions = self.get_mpe_processed_transactions_from_event_pub_sub(processing_txn)
            for txn in processed_transactions:
                if txn["processed"]:
                    txn_data = list(filter(lambda x: x.transaction_hash == txn["transactionHash"], processing_txns_db))[0]
                    txn_data.status = TransactionStatus.SUCCESS
                    channel_repo.update_channel_transaction_history_status(channel_txn_history=txn_data)
