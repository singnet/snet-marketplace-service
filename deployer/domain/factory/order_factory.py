from typing import Iterable

from deployer.domain.factory.transaction_factory import TransactionFactory
from deployer.domain.models.order import OrderDomain
from deployer.infrastructure.models import Order


class OrderFactory:
    @staticmethod
    def order_from_db_model(order_db_model: Order) -> OrderDomain:
        return OrderDomain(
            id=order_db_model.id,
            daemon_id=order_db_model.daemon_id,
            status=order_db_model.status,
            evm_transactions = TransactionFactory.transactions_from_db_model(order_db_model.evm_transactions),
            created_on = order_db_model.created_on,
            updated_on = order_db_model.updated_on
        )

    @staticmethod
    def orders_from_db_model(
            orders_db_model: Iterable[Order]
    ) -> list[OrderDomain]:
        return [
            OrderFactory.order_from_db_model(order_db_model)
            for order_db_model in orders_db_model
        ]
