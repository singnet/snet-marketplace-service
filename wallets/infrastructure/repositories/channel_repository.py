from datetime import datetime as dt
import json

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

from wallets.domain.models.channel_transaction_history import ChannelTransactionHistoryModel
from wallets.domain.models.create_channel_event import CreateChannelEventModel
from wallets.domain.models.user_wallet import UserWalletModel
from wallets.domain.models.wallet import WalletModel
from wallets.domain.wallets_factory import WalletsFactory
from wallets.infrastructure.models import ChannelTransactionHistory, CreateChannelEvent, UserWallet, Wallet
from wallets.infrastructure.repositories.base_repository import BaseRepository

from common.logger import get_logger
from common.constant import TransactionStatus


logger = get_logger(__name__)


class ChannelRepository(BaseRepository):

    def get_channel_transaction_history_data(self, transaction_hash=None, status=None):
        try:
            query = self.session.query(ChannelTransactionHistory)
            if transaction_hash:
                query = query.filter(ChannelTransactionHistory.transaction_hash == transaction_hash)
            if status:
                query = query.filter(ChannelTransactionHistory.status == status)
            channel_txn_history_db = query.all()
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to get channel transaction history data: {e}")
            raise e
        txn_history = []
        for history in channel_txn_history_db:
            txn_history.append(
                WalletsFactory().convert_channel_transaction_history_db_model_to_entity_model(history))
        return txn_history

    def update_channel_transaction_history_status_by_order_id(self, channel_txn_history):
        try:
            transaction_record_db = self.session.query(ChannelTransactionHistory). \
                filter(ChannelTransactionHistory.order_id == channel_txn_history.order_id). \
                first()
            if transaction_record_db:
                transaction_record_db.transaction_hash = channel_txn_history.transaction_hash,
                transaction_record_db.request_parameters = channel_txn_history.request_parameters,
                transaction_record_db.status = channel_txn_history.status,
                transaction_record_db.row_updated = dt.utcnow()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to update channel transaction history status: {e}")
            raise e

    def add_channel_transaction_history_record(self, channel_txn_history):
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

    def get_channel_transactions_for_username_recipient(self, username: str, org_id: str, group_id: str) -> list[tuple[UserWalletModel, WalletModel, ChannelTransactionHistoryModel]]:
        try:
            user_transactions = self.session.query(
                UserWallet, Wallet, ChannelTransactionHistory
            ).join(
                Wallet, UserWallet.address == Wallet.address
            ).outerjoin(
                ChannelTransactionHistory,
                and_(
                    UserWallet.address == ChannelTransactionHistory.address,
                    ChannelTransactionHistory.status != TransactionStatus.SUCCESS,
                    ChannelTransactionHistory.org_id == org_id,
                    ChannelTransactionHistory.group_id == group_id
                )
            ).filter(
                UserWallet.username == username
            ).all()

            result = []
            for user_transaction in user_transactions:
                user_wallet = WalletsFactory.convert_user_wallet_db_model_to_entity_model(user_transaction.UserWallet)
                wallet = WalletsFactory.convert_wallet_db_model_to_entity_model(user_transaction.Wallet)
                channel_txn = WalletsFactory.convert_channel_transaction_history_db_model_to_entity_model(user_transaction.ChannelTransactionHistory)
                result.append((user_wallet, wallet, channel_txn))
            return result

        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to get channel transactions: {e}")
            raise e

    def insert_channel_history(self, order_id, amount, currency, type, group_id, org_id, recipient,
                             address, signature, request_parameters, transaction_hash, status) -> bool:
        try:
            time_now = dt.utcnow()
            channel_txn = ChannelTransactionHistory(
                order_id=order_id,
                amount=amount,
                org_id=org_id,
                group_id=group_id,
                currency=currency,
                type=type,
                recipient=recipient,
                address=address,
                signature=signature,
                request_parameters=request_parameters,
                transaction_hash=transaction_hash,
                status=status,
                row_created=time_now,
                row_updated=time_now
            )
            self.session.add(channel_txn)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to insert channel history: {e}")
            return False

    def get_channel_transactions_against_order_id(self, order_id: str) -> list[ChannelTransactionHistoryModel]:
        try:
            transactions_data = self.session.query(ChannelTransactionHistory).filter_by(order_id = order_id).all()
            transactions = []
            for transaction in transactions_data:
                txn = WalletsFactory.convert_channel_transaction_history_db_model_to_entity_model(transaction)
                transactions.append(txn)
            return transactions
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to get channel transactions: {e}")
            raise e

    def persist_create_channel_event(self, payload, created_at) -> bool:
        try:
            event = CreateChannelEvent(
                payload=json.dumps(payload),
                row_created=created_at,
                row_updated=created_at,
                status=TransactionStatus.PENDING
            )
            self.session.add(event)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to persist create channel event: {e}")
            return False

    def get_one_create_channel_event(self, status: str) -> CreateChannelEventModel:
        try:
            event = self.session.query(
                CreateChannelEvent
            ).filter(
                CreateChannelEvent.status == status
            ).first()
            return WalletsFactory.convert_create_channel_event_db_model_to_entity_model(event) if event is not None else None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def update_create_channel_event(self, event_details, status: str) -> bool:
        try:
            result = self.session.query(CreateChannelEvent).filter(
                CreateChannelEvent.row_id == event_details["row_id"]
            ).update({
                "status": status
            })
            self.session.commit()
            return result == 1
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to update create channel event: {e}")
            return False
