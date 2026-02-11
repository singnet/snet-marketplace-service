from dataclasses import dataclass
from typing import List, Optional

from deployer.domain.models.base_domain import BaseDomain
from deployer.domain.models.evm_transaction import EVMTransactionDomain
from deployer.infrastructure.models import OrderStatus


@dataclass
class NewOrderDomain:
    id: str
    account_id: str
    status: OrderStatus
    amount: int


@dataclass
class OrderDomain(NewOrderDomain, BaseDomain):
    evm_transactions: Optional[List[EVMTransactionDomain]] = None

    def to_response(self, remove_created_updated: bool = True) -> dict:
        result = super().to_response(remove_created_updated)
        result["evmTransactions"] = [
            transaction.to_response() for transaction in self.evm_transactions
        ]
        return result

    def to_short_response(self):
        result = super().to_response()
        del result["evmTransactions"]
        return result
