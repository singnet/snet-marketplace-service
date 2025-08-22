from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from deployer.constant import TRANSACTION_TTL
from deployer.domain.factory.order_factory import OrderFactory
from deployer.domain.models.order import NewOrderDomain, OrderDomain
from deployer.infrastructure.models import Order, OrderStatus


class OrderRepository:
    @staticmethod
    def create_order(session: Session, order: NewOrderDomain) -> None:
        order_model = Order(
            id = order.id,
            daemon_id = order.daemon_id,
            status = order.status,
        )
        session.add(order_model)

    @staticmethod
    def update_order_status(session: Session, order_id: str, status: OrderStatus) -> None:
        update_query = update(
            Order
        ).where(
            Order.id == order_id
        ).values(
            status=status
        )

        session.execute(update_query)

    @staticmethod
    def get_order(session: Session, order_id: str) -> Optional[OrderDomain]:
        query = select(
            Order
        ).where(
            Order.id == order_id
        ).limit(1)

        result = session.execute(query)

        order_db = result.scalar_one_or_none()
        if order_db is None:
            return None

        return OrderFactory.order_from_db_model(order_db)

    @staticmethod
    def get_daemon_orders(session: Session, daemon_id: str) -> list[OrderDomain]:
        query = select(
            Order
        ).where(
            daemon_id == Order.daemon_id
        )
        result = session.execute(query)
        orders_db = result.scalars().all()

        return OrderFactory.orders_from_db_model(orders_db)

    @staticmethod
    def get_last_order(session: Session, daemon_id: str) -> Optional[OrderDomain]:
        query = select(
            Order
        ).where(
            daemon_id == Order.daemon_id
        ).order_by(
            Order.id.desc()
        ).limit(1)

        result = session.execute(query)

        order_db = result.scalar_one_or_none()
        if order_db is None:
            return None

        return OrderFactory.order_from_db_model(order_db)

    @staticmethod
    def fail_old_orders(session: Session) -> None:
        current_time = datetime.now(UTC)
        query = update(
            Order
        ).where(
            Order.status == OrderStatus.PROCESSING,
            Order.updated_at < current_time - TRANSACTION_TTL
        ).values(
            status = OrderStatus.FAILED
        )

        session.execute(query)
