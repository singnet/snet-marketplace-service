from typing import Optional

from sqlalchemy import select, update

from deployer.domain.factory.order_factory import OrderFactory
from deployer.domain.models.order import NewOrderDomain, OrderDomain
from deployer.infrastructure.db import BaseRepository
from deployer.infrastructure.models import Order


class OrderRepository(BaseRepository):
    def upsert_order(self, order: NewOrderDomain) -> None:
        query = (
            select(Order)
            .where(Order.id == order.id)
            .limit(1)
        )
        result = self.session.execute(query)
        order_db = result.scalar_one_or_none()

        if order_db is not None:
            update_query = (
                update(Order)
                .where(Order.id == order.id)
                .values(
                    status=order.status,
                )
            )
            self.session.execute(update_query)
        else:
            order_model = Order(
                id=order.id,
                daemon_id=order.daemon_id,
                status=order.status,
            )
            self.session.add(order_model)

    def get_order(self, order_id: str) -> Optional[OrderDomain]:
        query = (
            select(Order)
            .where(Order.id == order_id)
            .limit(1)
        )
        result = self.session.execute(query)
        order_db = result.scalar_one_or_none()

        if order_db is None:
            return None

        return OrderFactory.order_from_db_model(order_db)

    def get_all_orders(self) -> list[OrderDomain]:
        query = (
            select(Order)
        )
        result = self.session.execute(query)
        orders_db = result.scalars().all()

        return OrderFactory.orders_from_db_model(orders_db)