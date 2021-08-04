from wallets.domain.models.channel_transaction_history import ChannelTransactionHistory


class WalletFactory:

    @staticmethod
    def convert_channel_transaction_history_db_model_to_entity_model(channel_transaction_history_db):
        return ChannelTransactionHistory(
            order_id=channel_transaction_history_db.order_id,
            amount=channel_transaction_history_db.amount,
            currency=channel_transaction_history_db.currency,
            type=channel_transaction_history_db.type,
            address=channel_transaction_history_db.address,
            recipient=channel_transaction_history_db.recipient,
            signature=channel_transaction_history_db.signature,
            org_id=channel_transaction_history_db.org_id,
            group_id=channel_transaction_history_db.group_id,
            request_parameters=channel_transaction_history_db.request_parameters,
            transaction_hash=channel_transaction_history_db.transaction_hash,
            status=channel_transaction_history_db.status
        )
