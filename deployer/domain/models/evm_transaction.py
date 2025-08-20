from dataclasses import dataclass

from deployer.domain.models.base_domain import BaseDomain
from deployer.infrastructure.models import EvmTransactionStatus


@dataclass
class NewEVMTransactionDomain:
    hash: str
    order_id: str
    status: EvmTransactionStatus
    sender: str
    recipient: str


@dataclass
class EVMTransactionDomain(NewEVMTransactionDomain, BaseDomain):
    pass