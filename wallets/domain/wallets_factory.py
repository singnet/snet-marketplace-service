from wallets.domain.models.channel_transaction_history import ChannelTransactionHistoryModel
from wallets.domain.models.wallet import WalletModel
from wallets.domain.models.user_wallet import UserWalletModel
from wallets.domain.models.create_channel_event import CreateChannelEventModel


class WalletsFactory:

    @staticmethod
    def convert_channel_transaction_history_db_model_to_entity_model(channel_transaction_history_db):
        return ChannelTransactionHistoryModel(
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

    @staticmethod
    def convert_wallet_db_model_to_entity_model(wallet_db):
        return WalletModel(
            row_id=wallet_db.row_id,
            address=wallet_db.address,
            type=wallet_db.type,
            encrypted_key=wallet_db.encrypted_key,
            status=wallet_db.status
        )

    @staticmethod
    def convert_user_wallet_db_model_to_entity_model(user_wallet_db):
        return UserWalletModel(
            row_id=user_wallet_db.row_id,
            username=user_wallet_db.username,
            address=user_wallet_db.address,
            is_default=user_wallet_db.is_default
        )

    @staticmethod
    def convert_create_channel_event_db_model_to_entity_model(create_channel_event_db):
        return CreateChannelEventModel(
            row_id=create_channel_event_db.row_id,
            payload=create_channel_event_db.payload,
            status=create_channel_event_db.status
        )
