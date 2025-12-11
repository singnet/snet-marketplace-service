from datetime import datetime, UTC, timedelta
from typing import Optional, List, Dict

from sqlalchemy import select, update, func, and_
from sqlalchemy.orm import Session

from deployer.config import TRANSACTION_TTL_IN_MINUTES
from deployer.domain.factory.order_factory import OrderFactory
from deployer.domain.models.order import NewOrderDomain, OrderDomain
from deployer.infrastructure.models import Order, OrderStatus


class OrderRepository:
    @staticmethod
    def create_order(session: Session, order: NewOrderDomain) -> None:
        order_model = Order(
            id=order.id,
            daemon_id=order.daemon_id,
            status=order.status,
        )
        session.add(order_model)

    @staticmethod
    def update_order_status(session: Session, order_id: str, status: OrderStatus) -> None:
        update_query = update(Order).where(Order.id == order_id).values(status=status)

        session.execute(update_query)

    @staticmethod
    def get_order(session: Session, order_id: str) -> Optional[OrderDomain]:
        query = select(Order).where(Order.id == order_id).limit(1)

        result = session.execute(query)

        order_db = result.scalar_one_or_none()
        if order_db is None:
            return None

        return OrderFactory.order_from_db_model(order_db)

    @staticmethod
    def get_daemon_orders(session: Session, daemon_id: str) -> List[OrderDomain]:
        query = select(Order).where(daemon_id == Order.daemon_id)
        result = session.execute(query)
        orders_db = result.scalars().all()

        return OrderFactory.orders_from_db_model(orders_db)

    @staticmethod
    def get_last_successful_orders_batch(
        session: Session, daemon_ids: List[str]
    ) -> Dict[str, OrderDomain]:
        if not daemon_ids:
            return {}

        subquery = (
            select(Order.daemon_id, func.max(Order.updated_at).label("max_updated_at"))
            .where(Order.daemon_id.in_(daemon_ids), Order.status == OrderStatus.SUCCESS)
            .group_by(Order.daemon_id)
            .subquery()
        )

        query = select(Order).join(
            subquery,
            and_(
                Order.daemon_id == subquery.c.daemon_id,
                Order.updated_at == subquery.c.max_updated_at,
            ),
        )

        result = session.execute(query)
        orders_db = result.scalars().all()

        orders = {}
        for order_db in orders_db:
            order = OrderFactory.order_from_db_model(order_db)
            orders[order.daemon_id] = order

        return orders

    @staticmethod
    def get_last_order(session: Session, daemon_id: str) -> Optional[OrderDomain]:
        query = (
            select(Order)
            .where(Order.daemon_id == daemon_id)
            .order_by(Order.updated_at.desc())
            .limit(1)
        )

        result = session.execute(query)

        order_db = result.scalar_one_or_none()
        if order_db is None:
            return None

        return OrderFactory.order_from_db_model(order_db)

    @staticmethod
    def fail_old_orders(session: Session) -> None:
        current_time = datetime.now(UTC)
        query = (
            update(Order)
            .where(
                Order.status == OrderStatus.PROCESSING,
                Order.updated_at < current_time - timedelta(minutes=TRANSACTION_TTL_IN_MINUTES),
            )
            .values(status=OrderStatus.FAILED)
        )

        session.execute(query)
