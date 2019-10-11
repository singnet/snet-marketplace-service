from common.blockchain_util import BlockChainUtil
from common.constant import TransactionStatus
from wallets.dao.channel_transaction_status_data_access_object import \
    ChannelTransactionStatusDataAccessObject
from wallets.config import NETWORKS, NETWORK_ID


class ChannelTransactionStatusService:
    def __init__(self, repo, net_id):
        self.net_id = net_id
        self.repo = repo
        self.obj_blockchain_util = BlockChainUtil(provider_type="HTTP_PROVIDER",
                                                  provider=NETWORKS[NETWORK_ID]['http_provider'])
        self.obj_channel_transaction_history_dao = ChannelTransactionStatusDataAccessObject(repo=self.repo)

    def manage_channel_transaction_status(self):
        transaction_data = self.obj_channel_transaction_history_dao.get_pending_transaction_data()
        print(transaction_data)
        for transaction_record in transaction_data:
            transaction_hash = transaction_record['transaction_hash']
            transaction_receipt = self.obj_blockchain_util.get_transaction_receipt_from_blockchain(
                transaction_hash=transaction_hash)
            if transaction_receipt is not None:
                status = TransactionStatus.SUCCESS if transaction_receipt.status == 1 else TransactionStatus.FAILED
                self.obj_channel_transaction_history_dao.update_channel_transaction_history(
                    transaction_hash=transaction_hash, status=status)
