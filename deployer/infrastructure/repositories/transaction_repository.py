from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import update, select
from sqlalchemy.orm import Session

from deployer.constant import TRANSACTION_TTL
from deployer.domain.factory.transaction_factory import TransactionFactory
from deployer.domain.models.evm_transaction import NewEVMTransactionDomain, EVMTransactionDomain
from deployer.domain.models.transactions_metadata import TransactionsMetadataDomain
from deployer.infrastructure.models import EVMTransaction, TransactionsMetadata, EVMTransactionStatus


class TransactionRepository:
    @staticmethod
    def upsert_transaction(session: Session, transaction: NewEVMTransactionDomain) -> None:
        query = select(
            EVMTransaction
        ).where(
            EVMTransaction.hash == transaction.hash
        ).limit(1)

        result = session.execute(query)
        transaction_db = result.scalar_one_or_none()

        if transaction_db is not None:
            query = update(
                EVMTransaction
            ).where(
                EVMTransaction.hash == transaction.hash
            ).values(
                status=transaction.status
            )

            session.execute(query)
        else:
            transaction_db = EVMTransaction(
                hash=transaction.hash,
                order_id=transaction.order_id,
                status=transaction.status
            )

            session.add(transaction_db)

    @staticmethod
    def get_transaction(session: Session, transaction_hash: str) -> Optional[EVMTransactionDomain]:
        query = select(
            EVMTransaction
        ).where(
            EVMTransaction.hash == transaction_hash
        )

        result = session.execute(query)
        transaction_db = result.scalar_one_or_none()

        if transaction_db is None:
            return None

        return TransactionFactory.transaction_from_db_model(transaction_db)

    @staticmethod
    def get_transactions_metadata(session: Session) -> list[TransactionsMetadataDomain]:
        query = select(TransactionsMetadata)

        result = session.execute(query)
        transactions_metadata_db = result.scalars().all()

        return TransactionFactory.transactions_metadata_list_from_db_model(transactions_metadata_db)

    @staticmethod
    def update_transactions_metadata(session: Session, metadata_id: int, last_block_no: int) -> None:
        update_query = update(
            TransactionsMetadata
        ).where(
            TransactionsMetadata.id == metadata_id
        ).values(
            last_block_no=last_block_no
        )

        session.execute(update_query)

    @staticmethod
    def fail_old_transactions(session: Session) -> None:
        current_time = datetime.now(UTC)
        query = update(
            EVMTransaction
        ).where(
            EVMTransaction.status == EVMTransactionStatus.PENDING,
            EVMTransaction.updated_on < current_time - TRANSACTION_TTL
        ).values(
            status = EVMTransactionStatus.FAILED
        )

        session.execute(query)
