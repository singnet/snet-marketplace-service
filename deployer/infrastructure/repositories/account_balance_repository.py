from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from deployer.domain.factory.account_balance_factory import AccountBalanceFactory
from deployer.domain.models.account_balance import AccountBalanceDomain, NewAccountBalanceDomain
from deployer.infrastructure.models import AccountBalance


class AccountBalanceRepository:
    @staticmethod
    def get_account_balance(session: Session, account_id: str) -> Optional[AccountBalanceDomain]:
        query = select(AccountBalance).where(AccountBalance.account_id == account_id).limit(1)

        result = session.execute(query)

        account_balance_db = result.scalar_one_or_none()

        if account_balance_db is None:
            return None

        return AccountBalanceFactory.account_balance_from_db_model(account_balance_db)

    @staticmethod
    def upsert_account_balance(session: Session, account_balance: NewAccountBalanceDomain) -> None:
        query = select(AccountBalance).where(AccountBalance.account_id == account_balance.account_id).limit(1)

        result = session.execute(query)
        account_balance_db = result.scalar_one_or_none()

        if account_balance_db is not None:
            query = (
                update(AccountBalance)
                .where(AccountBalance.account_id == account_balance.account_id)
                .values(balance_in_cogs=account_balance.balance_in_cogs)
            )

            session.execute(query)
        else:
            account_balance_db = AccountBalance(
                account_id=account_balance.account_id,
                balance_in_cogs=account_balance.balance_in_cogs
            )

            session.add(account_balance_db)

    @staticmethod
    def increase_account_balance(session: Session, account_id: str, amount: int) -> None:
        query = update(AccountBalance).where(AccountBalance.account_id == account_id).values(balance_in_cogs = AccountBalance.balance_in_cogs + amount)

        session.execute(query)

    @staticmethod
    def decrease_account_balance(session: Session, account_id: str, amount: int) -> None:
        query = update(AccountBalance).where(AccountBalance.account_id == account_id).values(
            balance_in_cogs = AccountBalance.balance_in_cogs - amount)

        session.execute(query)


