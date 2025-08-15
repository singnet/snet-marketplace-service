from deployer.application.schemas.transaction_schemas import SaveEVMTransactionRequest, GetTransactionsRequest
from deployer.domain.models.evm_transaction import NewEVMTransactionDomain
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository


class TransactionService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory

    def save_evm_transaction(self, request: SaveEVMTransactionRequest):
        with session_scope(self.session_factory) as session:
            TransactionRepository.upsert_transaction(
                session,
                NewEVMTransactionDomain(
                    hash=request.transaction_hash,
                    order_id=request.order_id,
                    status=request.status
                )
            )

    def get_transactions(self, request: GetTransactionsRequest, username: str):
        pass
