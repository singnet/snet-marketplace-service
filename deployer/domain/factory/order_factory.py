from typing import Iterable, List

from deployer.domain.factory.transaction_factory import TransactionFactory
from deployer.domain.models.order import OrderDomain
from deployer.infrastructure.models import Order


class OrderFactory:
    @staticmethod
    def order_from_db_model(order_db_model: Order) -> OrderDomain:
        return OrderDomain(
            id=order_db_model.id,
            account_id=order_db_model.account_id,
            status=order_db_model.status,
            amount=order_db_model.amount,
            evm_transactions=TransactionFactory.transactions_from_db_model(
                order_db_model.evm_transactions
            ),
            created_at=order_db_model.created_at,
            updated_at=order_db_model.updated_at,
        )

    @staticmethod
    def orders_from_db_model(orders_db_model: Iterable[Order]) -> List[OrderDomain]:
        return [
            OrderFactory.order_from_db_model(order_db_model) for order_db_model in orders_db_model
        ]
