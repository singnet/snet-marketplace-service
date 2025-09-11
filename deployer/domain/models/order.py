from dataclasses import dataclass
from typing import List

from deployer.domain.models.base_domain import BaseDomain
from deployer.domain.models.evm_transaction import EVMTransactionDomain
from deployer.infrastructure.models import OrderStatus


@dataclass
class NewOrderDomain:
    id: str
    daemon_id: str
    status: OrderStatus


@dataclass
class OrderDomain(NewOrderDomain, BaseDomain):
    evm_transactions: List[EVMTransactionDomain] | None = None

    def to_response(self):
        result = super().to_response()
        result["updatedAt"] = self.updated_at.isoformat()

        result["evmTransactions"] = []
        for transaction in self.evm_transactions:
            transaction_result = transaction.to_response()
            transaction_result["updatedAt"] = transaction.updated_at.isoformat()
            result["evmTransactions"].append(transaction_result)

        return result

    def to_short_response(self):
        result = super().to_response()
        del result["evmTransactions"]
        return result
