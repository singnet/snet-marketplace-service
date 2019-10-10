from common.constant import TransactionStatus


class ChannelTransactionStatusDataAccessObject:
    def __init__(self, repo):
        self.repo = repo

    def get_pending_transaction_data(self):
        raw_transaction_data = self.repo.execute(
            "SELECT transaction_hash FROM channel_transaction_history WHERE status = %s",
            [TransactionStatus.PENDING])
        return raw_transaction_data

    def update_channel_transaction_history(self, transaction_hash, status):
        query_response = self.repo.execute(
            "UPDATE channel_transaction_history SET status = %s WHERE transaction_hash = %s ", [status,
                                                                                                transaction_hash])
        if query_response[0] == 1:
            print("Transaction with transaction hash %s got updated to status %s", transaction_hash, status)
