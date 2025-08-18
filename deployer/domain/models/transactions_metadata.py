from dataclasses import dataclass

from deployer.domain.models.base_domain import BaseDomain


@dataclass
class NewTransactionMetadata:
    id: int
    recipient: str
    last_block_no: int
    fetch_limit: int
    block_adjustment: int


@dataclass
class TransactionsMetadata(NewTransactionMetadata, BaseDomain):
    pass