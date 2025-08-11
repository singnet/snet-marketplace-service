from dataclasses import dataclass

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
    evm_transactions: list[EVMTransactionDomain] | None = None