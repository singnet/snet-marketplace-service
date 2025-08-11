from sqlalchemy import select, update
from sqlalchemy.orm import Session

from deployer.domain.models.order import NewOrderDomain, OrderDomain
from deployer.infrastructure.models import Order


class OrderRepository:
    def upsert_order(self, session: Session, order: NewOrderDomain) -> None:
        query = (
            select(Order)
            .where(Order.id == order.id)
            .limit(1)
        )
        result = session.execute(query)
        order_db = result.scalar_one_or_none()

        if order_db is not None:
            update_query = (
                update(Order)
                .where(Order.id == order.id)
                .values(
                    daemon_id=order.daemon_id,
                    status=order.status,
                )
            )
            session.execute(update_query)
        else:
            order_model = Order(
                id=order.id,
                daemon_id=order.daemon_id,
                status=order.status,
            )
            session.add(order_model)

    def get_order(self, session: Session, order_id: str) -> OrderDomain:
        query = (
            select(Order)
            .where(Order.id == order_id)
            .limit(1)
        )
        result = session.execute(query)
        order_db = result.scalar_one_or_none()

        return OrderDomain(
            id=order_db.id,
            daemon_id=order_db.daemon_id,
            status=order_db.status,
        )

    def get_all_orders(self, session: Session):
        pass