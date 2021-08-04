from wallets.domain.models.channel_transaction_history import ChannelTransactionHistory


class WalletFactory:

    @staticmethod
    def convert_channel_transaction_history_db_model_to_entity_model(channel_transaction_history):
        if not channel_transaction_history:
            return None
        return ChannelTransactionHistory(
            order_id=channel_transaction_history.order_id,
            amount=channel_transaction_history.amount,
            currency=channel_transaction_history.currency,
            type=channel_transaction_history.type,
            address=channel_transaction_history.address,
            recipient=channel_transaction_history.recipient,
            signature=channel_transaction_history.signature,
            org_id=channel_transaction_history.org_id,
            group_id=channel_transaction_history.group_id,
            request_parameters=channel_transaction_history.request_parameters,
            transaction_hash=channel_transaction_history.transaction_hash,
            status=channel_transaction_history.status
        )
