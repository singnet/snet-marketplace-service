from dataclasses import dataclass

from deployer.domain.models.base_domain import BaseDomain


@dataclass
class NewAccountBalanceDomain:
    account_id: str
    balance_in_cogs: int


@dataclass
class AccountBalanceDomain(NewAccountBalanceDomain, BaseDomain):
    def to_response(self, remove_timestamps: bool = False):
        return {"balanceInCogs": self.balance_in_cogs}
