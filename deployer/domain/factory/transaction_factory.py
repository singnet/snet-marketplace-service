from typing import Iterable

from deployer.domain.models.evm_transaction import EVMTransactionDomain
from deployer.infrastructure.models import EVMTransaction


class TransactionFactory:
    @staticmethod
    def transaction_from_db_model(
            transaction_db_model: EVMTransaction
    ) -> EVMTransactionDomain:
        return EVMTransactionDomain(
            hash=transaction_db_model.hash,
            order_id=transaction_db_model.order_id,
            status=transaction_db_model.status,
            created_on=transaction_db_model.created_on,
            updated_on=transaction_db_model.updated_on
        )

    @staticmethod
    def transactions_from_db_model(
            transactions_db_model: Iterable[EVMTransaction]
    ) -> list[EVMTransactionDomain]:
        return [
            TransactionFactory.transaction_from_db_model(transaction_db_model)
            for transaction_db_model in transactions_db_model
        ]