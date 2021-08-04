from wallets.domain.models.channel_transaction_history import ChannelTransactionHistory
from wallets.infrastructure.repositories.channel_repository import ChannelRepository

channel_repo = ChannelRepository()


class ChannelService:

    @staticmethod
    def add_or_update_channel_transaction_history(transaction_record):
        record = ChannelTransactionHistory(
            order_id=transaction_record["order_id"],
            amount=transaction_record.get("amount", 0),
            currency=transaction_record.get("currency", ""),
            type=transaction_record.get("type", ""),
            address=transaction_record.get("address", ""),
            recipient=transaction_record.get("recipient", ""),
            signature=transaction_record.get("signature", ""),
            org_id=transaction_record["org_id"],
            group_id=transaction_record["group_id"],
            request_parameters=transaction_record.get("request_parameters", ""),
            transaction_hash=transaction_record.get("transaction_hash", ""),
            status=transaction_record.get("status", )
        )
        transaction_record = channel_repo.add_or_update_channel_transaction_history(record)
        return transaction_record.to_dict()
