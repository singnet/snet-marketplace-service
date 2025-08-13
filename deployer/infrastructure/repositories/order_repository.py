from typing import Optional

from sqlalchemy import select, update

from deployer.domain.factory.order_factory import OrderFactory
from deployer.domain.models.order import NewOrderDomain, OrderDomain
from deployer.infrastructure.db import BaseRepository
from deployer.infrastructure.models import Order, OrderStatus


class OrderRepository(BaseRepository):
    def create_order(self, order: NewOrderDomain) -> None:
        order_model = Order(
            id = order.id,
            daemon_id = order.daemon_id,
            status = order.status,
        )
        self.session.add(order_model)

    def update_order_status(self, order_id: str, status: OrderStatus) -> None:
        update_query = update(
            Order
        ).where(
            Order.id == order_id
        ).values(
            status=status
        )

        self.session.execute(update_query)

    def get_order(self, order_id: str) -> Optional[OrderDomain]:
        query = select(
            Order
        ).where(
            Order.id == order_id
        ).limit(1)

        result = self.session.execute(query)

        order_db = result.scalar_one_or_none()
        if order_db is None:
            return None

        return OrderFactory.order_from_db_model(order_db)

    def get_daemon_orders(self, daemon_id: str) -> list[OrderDomain]:
        query = select(
            Order
        ).where(
            daemon_id == Order.daemon_id
        )
        result = self.session.execute(query)
        orders_db = result.scalars().all()

        return OrderFactory.orders_from_db_model(orders_db)