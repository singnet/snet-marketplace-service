from datetime import datetime as dt

from sqlalchemy.exc import SQLAlchemyError

from wallets.domain.factory.wallet_factory import WalletFactory
from wallets.infrastructure.models import ChannelTransactionHistory
from wallets.infrastructure.repositories.base_repository import BaseRepository


class ChannelRepository(BaseRepository):
    pass

    def get_channel_transaction_history_data(self, transaction_hash=None, status=None):
        try:
            query = self.session.query(ChannelTransactionHistory)
            if transaction_hash:
                query = query.filter(ChannelTransactionHistory.transaction_hash == transaction_hash)
            if status:
                query = query.filter(ChannelTransactionHistory.status == status)
            channel_txn_history_db = query.all()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        txn_history = []
        for history in channel_txn_history_db:
            txn_history.append(
                WalletFactory().convert_channel_transaction_history_db_model_to_entity_model(history))
        return txn_history

    def update_channel_transaction_history_status(self, channel_txn_history):
        try:
            transaction_record_db = self.session.query(ChannelTransactionHistory). \
                filter(ChannelTransactionHistory.transaction_hash == channel_txn_history.transaction_hash). \
                filter(ChannelTransactionHistory.org_id == channel_txn_history.org_id).  \
                filter(ChannelTransactionHistory.group_id == channel_txn_history.group_id). \
                filter(ChannelTransactionHistory.order_id == channel_txn_history.order_id).  \
                first()
            if transaction_record_db:
                transaction_record_db.order_id = channel_txn_history.order_id,
                transaction_record_db.amount = channel_txn_history.amount,
                transaction_record_db.currency = channel_txn_history.currency,
                transaction_record_db.type = channel_txn_history.type,
                transaction_record_db.transaction_hash = channel_txn_history.transaction_hash,
                transaction_record_db.address = channel_txn_history.address,
                transaction_record_db.recipient = channel_txn_history.recipient,
                transaction_record_db.signature = channel_txn_history.signature,
                transaction_record_db.org_id = channel_txn_history.org_id,
                transaction_record_db.group_id = channel_txn_history.group_id,
                transaction_record_db.request_parameters = channel_txn_history.request_parameters,
                transaction_record_db.status = channel_txn_history.status,
                transaction_record_db.row_updated = dt.utcnow()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        if not transaction_record_db:
            self.add_item(ChannelTransactionHistory(
                order_id=channel_txn_history.order_id,
                amount=channel_txn_history.amount,
                currency=channel_txn_history.currency,
                type=channel_txn_history.type,
                address=channel_txn_history.address,
                recipient=channel_txn_history.recipient,
                signature=channel_txn_history.signature,
                org_id=channel_txn_history.org_id,
                group_id=channel_txn_history.group_id,
                request_parameters=channel_txn_history.request_parameters,
                transaction_hash=channel_txn_history.transaction_hash,
                status=channel_txn_history.status,
                row_updated=dt.utcnow(),
                row_created=dt.utcnow()
            ))
        return channel_txn_history



