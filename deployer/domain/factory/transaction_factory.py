from typing import Iterable

from deployer.domain.models.evm_transaction import EVMTransactionDomain, NewEVMTransactionDomain
from deployer.domain.models.transactions_metadata import TransactionsMetadataDomain
from deployer.infrastructure.models import EVMTransaction, TransactionsMetadata


class TransactionFactory:
    @staticmethod
    def new_transaction_from_blockchain_event() -> NewEVMTransactionDomain:
        pass

    @staticmethod
    def transaction_from_db_model(
            transaction_db_model: EVMTransaction
    ) -> EVMTransactionDomain:
        return EVMTransactionDomain(
            hash=transaction_db_model.hash,
            order_id=transaction_db_model.order_id,
            status=transaction_db_model.status,
            sender=transaction_db_model.sender,
            recipient=transaction_db_model.recipient,
            created_at =transaction_db_model.created_at,
            updated_at =transaction_db_model.updated_at
        )

    @staticmethod
    def transactions_from_db_model(
            transactions_db_model: Iterable[EVMTransaction]
    ) -> list[EVMTransactionDomain]:
        return [
            TransactionFactory.transaction_from_db_model(transaction_db_model)
            for transaction_db_model in transactions_db_model
        ]

    @staticmethod
    def transactions_metadata_from_db_model(
            transactions_metadata_db_model: TransactionsMetadata
    ) -> TransactionsMetadataDomain:
        return TransactionsMetadataDomain(
            id=transactions_metadata_db_model.id,
            recipient=transactions_metadata_db_model.recipient,
            last_block_no=transactions_metadata_db_model.last_block_no,
            fetch_limit=transactions_metadata_db_model.fetch_limit,
            block_adjustment=transactions_metadata_db_model.block_adjustment,
            created_at =transactions_metadata_db_model.created_at,
            updated_at =transactions_metadata_db_model.updated_at
        )

    @staticmethod
    def transactions_metadata_list_from_db_model(
            transactions_db_model: Iterable[TransactionsMetadata]
    ) -> list[TransactionsMetadataDomain]:
        return [
            TransactionFactory.transactions_metadata_from_db_model(transaction_db_model)
            for transaction_db_model in transactions_db_model
        ]