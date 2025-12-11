from dataclasses import dataclass

from deployer.domain.models.base_domain import BaseDomain


@dataclass
class NewTransactionsMetadataDomain:
    id: int
    recipient: str
    last_block_no: int
    fetch_limit: int
    block_adjustment: int


@dataclass
class TransactionsMetadataDomain(NewTransactionsMetadataDomain, BaseDomain):
    pass
