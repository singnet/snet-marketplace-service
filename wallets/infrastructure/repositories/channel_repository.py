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
            channel_transaction_history_db = query.all()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        transaction_history = []
        for history in channel_transaction_history_db:
            transaction_history.append(
                WalletFactory().convert_channel_transaction_history_db_model_to_entity_model(history))
        return transaction_history

    def update_channel_transaction_history_status(self, transaction_hash, status):
        try:
            transaction_data = self.session.query(ChannelTransactionHistory). \
                filter(ChannelTransactionHistory.transaction_hash == transaction_hash). \
                first()
            if transaction_data:
                transaction_data.status = status
                transaction_data.row_updated = dt.utcnow()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def add_or_update_channel_transaction_history(self, record):
        try:
            transaction_record_db = self.session.query(ChannelTransactionHistory).\
                filter(ChannelTransactionHistory.org_id == record.org_id).\
                filter(ChannelTransactionHistory.group_id == record.group_id).\
                filter(ChannelTransactionHistory.order_id == record.order_id).\
                first()
            if transaction_record_db:
                transaction_record_db.order_id = record.order_id,
                transaction_record_db.amount = record.amount,
                transaction_record_db.currency = record.currency,
                transaction_record_db.type = record.type,
                transaction_record_db.transaction_hash = record.transaction_hash,
                transaction_record_db.address = record.address,
                transaction_record_db.recipient = record.recipient,
                transaction_record_db.signature = record.signature,
                transaction_record_db.org_id = record.org_id,
                transaction_record_db.group_id = record.group_id,
                transaction_record_db.request_parameters = record.request_parameters,
                transaction_record_db.status = record.status,
                transaction_record_db.row_updated = dt.utcnow()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        if not transaction_record_db:
            self.add_item(ChannelTransactionHistory(
                order_id=record.order_id,
                amount=record.amount,
                currency=record.currency,
                type=record.type,
                address=record.address,
                recipient=record.recipient,
                signature=record.signature,
                org_id=record.org_id,
                group_id=record.group_id,
                request_parameters=record.request_parameters,
                transaction_hash=record.transaction_hash,
                status=record.status,
                row_updated=dt.utcnow(),
                row_created=dt.utcnow()
            ))
        return record
