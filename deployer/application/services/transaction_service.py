from deployer.application.schemas.transaction_schemas import SaveEVMTransactionRequest, GetTransactionsRequest
from deployer.domain.models.evm_transaction import NewEVMTransactionDomain
from deployer.infrastructure.db import in_session
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository


class TransactionService:
    def __init__(self):
        self._transaction_repo = TransactionRepository()

    @in_session
    def save_evm_transaction(self, request: SaveEVMTransactionRequest):
        self._transaction_repo.upsert_transaction(
            NewEVMTransactionDomain(
                hash=request.transaction_hash,
                order_id=request.order_id,
                status=request.status
            )
        )

    @in_session
    def get_transactions(self, request: GetTransactionsRequest, username: str):
        pass
