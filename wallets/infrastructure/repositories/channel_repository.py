from datetime import datetime as dt

from sqlalchemy.exc import SQLAlchemyError

from wallets.domain.factory.wallet_factory import WalletFactory
from wallets.infrastructure.models import ChannelTransactionHistory
from wallets.infrastructure.repositories.base_repository import BaseRepository


class ChannelRepository(BaseRepository):
    pass

    def get_channel_transaction_history_data(self, status=None):
        try:
            query = self.session.query(ChannelTransactionHistory)
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
