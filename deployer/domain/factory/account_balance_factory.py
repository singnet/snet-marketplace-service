from deployer.domain.models.account_balance import AccountBalanceDomain
from deployer.infrastructure.models import AccountBalance


class AccountBalanceFactory:
    @staticmethod
    def account_balance_from_db_model(account_balance_db_model: AccountBalance) -> AccountBalanceDomain:
        return AccountBalanceDomain(
            account_id=account_balance_db_model.account_id,
            balance_in_cogs=account_balance_db_model.balance_in_cogs,
            created_at=account_balance_db_model.created_at,
            updated_at=account_balance_db_model.updated_at
        )