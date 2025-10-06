from datetime import datetime, UTC, timedelta
from typing import Optional, List, Union

from sqlalchemy import select, update, func
from sqlalchemy.orm import Session

from contract_api.constant import SortOrder
from deployer.config import TRANSACTION_TTL_IN_MINUTES
from deployer.constant import PeriodType, PERIOD_TYPE_TIMEDELTA
from deployer.domain.factory.order_factory import OrderFactory
from deployer.domain.models.order import NewOrderDomain, OrderDomain
from deployer.infrastructure.models import Order, OrderStatus


class OrderRepository:
    @staticmethod
    def get_orders(
        session: Session,
        account_id: str,
        limit: int,
        page: int,
        order: str,
        period: str,
        status: Union[OrderStatus, List[OrderStatus], None] = None,
    ) -> List[OrderDomain]:
        query = select(Order).where(Order.account_id == account_id)

        if status is not None:
            if isinstance(status, list):
                query = query.where(Order.status.in_(status))
            else:
                query = query.where(Order.status == status)

        if period != PeriodType.ALL:
            current_time = datetime.now(UTC)
            query = query.where(
                Order.updated_at > current_time - PERIOD_TYPE_TIMEDELTA[PeriodType(period)]
            )

        if order == SortOrder.ASC:
            query = query.order_by(Order.updated_at.asc())
        else:
            query = query.order_by(Order.updated_at.desc())

        query = query.limit(limit).offset((page - 1) * limit)

        result = session.execute(query)
        orders_db = result.scalars().all()

        return OrderFactory.orders_from_db_model(orders_db)

    @staticmethod
    def get_orders_total_count(
        session: Session,
        account_id: str,
        period: str,
        status: Union[OrderStatus, List[OrderStatus], None] = None,
    ) -> int:
        query = select(func.count()).select_from(Order).where(Order.account_id == account_id)

        if status is not None:
            if isinstance(status, list):
                query = query.where(Order.status.in_(status))
            else:
                query = query.where(Order.status == status)

        if period != PeriodType.ALL:
            current_time = datetime.now(UTC)
            query = query.where(
                Order.updated_at > current_time - PERIOD_TYPE_TIMEDELTA[PeriodType(period)]
            )

        result = session.execute(query)

        return result.scalar()

    @staticmethod
    def get_order(
        session: Session,
        order_id: Optional[str] = None,
        account_id: Optional[str] = None,
        status: Optional[OrderStatus] = None,
    ) -> Optional[OrderDomain]:
        query = select(Order)

        if order_id is not None:
            query = query.where(Order.id == order_id)
        if account_id is not None:
            query = query.where(Order.account_id == account_id)
        if status is not None:
            query = query.where(Order.status == status)

        query = query.order_by(Order.updated_at.desc()).limit(1)

        result = session.execute(query)

        order_db = result.scalar_one_or_none()
        if order_db is None:
            return None

        return OrderFactory.order_from_db_model(order_db)

    @staticmethod
    def create_order(session: Session, order: NewOrderDomain) -> None:
        order_model = Order(
            id=order.id,
            account_id=order.account_id,
            amount=order.amount,
            status=order.status,
        )
        session.add(order_model)

    @staticmethod
    def update_order_status(session: Session, order_id: str, status: OrderStatus) -> None:
        update_query = update(Order).where(Order.id == order_id).values(status=status)

        session.execute(update_query)

    @staticmethod
    def fail_old_orders(session: Session) -> None:
        current_time = datetime.now(UTC)
        query = (
            update(Order)
            .where(
                Order.status == OrderStatus.PROCESSING,
                Order.updated_at < current_time - timedelta(minutes=TRANSACTION_TTL_IN_MINUTES),
            )
            .values(status=OrderStatus.PAYMENT_FAILED)
        )

        session.execute(query)

    @staticmethod
    def expire_old_orders(session: Session) -> None:
        current_time = datetime.now(UTC)
        query = (
            update(Order)
            .where(
                Order.status == OrderStatus.CREATED,
                Order.updated_at < current_time - timedelta(minutes=TRANSACTION_TTL_IN_MINUTES),
            )
            .values(status=OrderStatus.EXPIRED)
        )

        session.execute(query)
