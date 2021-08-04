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
        pending_txns = [txn.transaction_hash for txn in pending_txns_db]
        logger.info(f"Pending transactions :: {pending_txns}")
        for txn_hash in pending_txns:
            txn_receipt = obj_blockchain_util.get_transaction_receipt_from_blockchain(
                transaction_hash=txn_hash)
            if txn_hash is not None:
                new_status = TransactionStatus.PROCESSING if txn_receipt.status == 1 else TransactionStatus.FAILED
                channel_repo.update_channel_transaction_history_status(
                    transaction_hash=txn_hash,
                    status=new_status
                )
        # UPDATE PROCESSING TRANSACTIONS
        processing_txns_db = channel_repo.get_channel_transaction_history_data(status=TransactionStatus.PROCESSING)
        processing_txns = [txn.transaction_hash for txn in processing_txns_db]
        logger.info(f"Processing transactions :: {processing_txns}")
        if processing_txns:
            processed_transactions = self.get_mpe_processed_transactions_from_event_pub_sub(processing_txns)
            for txn in processed_transactions:
                if txn["processed"]:
                    channel_repo.update_channel_transaction_history_status(
                        transaction_hash=txn["transactionHash"],
                        status=TransactionStatus.SUCCESS
                    )

