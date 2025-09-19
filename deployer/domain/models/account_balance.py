from dataclasses import dataclass

from deployer.domain.models.base_domain import BaseDomain


@dataclass
class NewAccountBalance:
    account_id: str
    balance_in_cogs: int


@dataclass
class AccountBalance(NewAccountBalance, BaseDomain):
    def to_response(self):
        return {"balanceInCogs": self.balance_in_cogs}
