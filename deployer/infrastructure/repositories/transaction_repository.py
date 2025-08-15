from sqlalchemy import update, select
from sqlalchemy.orm import Session

from deployer.domain.models.evm_transaction import NewEVMTransactionDomain
from deployer.infrastructure.models import EVMTransaction


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
