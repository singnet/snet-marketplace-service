from datetime import datetime
from typing import Optional, List

from sqlalchemy import update, select
from sqlalchemy.orm import Session

from deployer.domain.factory.daemon_factory import DaemonFactory
from deployer.domain.models.daemon import NewDaemonDomain, DaemonDomain
from deployer.infrastructure.models import Daemon, DaemonStatus, Order


class DaemonRepository:
    @staticmethod
    def create_daemon(session: Session, daemon: NewDaemonDomain) -> None:
        daemon_model = Daemon(
            id=daemon.id,
            account_id=daemon.account_id,
            org_id=daemon.org_id,
            service_id=daemon.service_id,
            status=daemon.status,
            daemon_config=daemon.daemon_config,
            start_at=daemon.start_at,
            end_at=daemon.end_at,
            service_published=False,
            daemon_endpoint=daemon.daemon_endpoint,
        )

        session.add(daemon_model)

    @staticmethod
    def update_daemon_status(session: Session, daemon_id: str, status: DaemonStatus) -> None:
        update_query = update(Daemon).where(Daemon.id == daemon_id).values(status=status)

        session.execute(update_query)

    @staticmethod
    def update_daemon_end_on(session: Session, daemon_id: str, end_on: datetime) -> None:
        update_query = update(Daemon).where(Daemon.id == daemon_id).values(end_on=end_on)

        session.execute(update_query)

    @staticmethod
    def update_daemon_config(session: Session, daemon_id: str, daemon_config: dict) -> None:
        update_query = (
            update(Daemon).where(Daemon.id == daemon_id).values(daemon_config=daemon_config)
        )

        session.execute(update_query)

    @staticmethod
    def update_daemon_service_published(
        session: Session, daemon_id: str, service_published: bool
    ) -> None:
        update_query = (
            update(Daemon).where(Daemon.id == daemon_id).values(service_published=service_published)
        )

        session.execute(update_query)

    @staticmethod
    def get_daemon(session: Session, daemon_id: str) -> Optional[DaemonDomain]:
        query = select(Daemon).where(Daemon.id == daemon_id).limit(1)

        result = session.execute(query)

        daemon_db = result.scalar_one_or_none()
        if daemon_db is None:
            return None

        return DaemonFactory.daemon_from_db_model(daemon_db)

    @staticmethod
    def get_user_daemons(session: Session, account_id: str) -> List[DaemonDomain]:
        query = select(Daemon).where(Daemon.account_id == account_id)

        result = session.execute(query)
        daemons_db = result.scalars().all()

        return DaemonFactory.daemons_from_db_model(daemons_db)

    @staticmethod
    def search_daemon(session: Session, org_id: str, service_id: str) -> Optional[DaemonDomain]:
        query = (
            select(Daemon).where(Daemon.org_id == org_id, Daemon.service_id == service_id).limit(1)
        )

        result = session.execute(query)

        daemon_db = result.scalar_one_or_none()
        if daemon_db is None:
            return None

        return DaemonFactory.daemon_from_db_model(daemon_db)

    @staticmethod
    def get_daemons_without_statuses(
        session: Session, statuses: List[DaemonStatus]
    ) -> List[DaemonDomain]:
        query = select(Daemon).where(Daemon.status.notin_(statuses))

        result = session.execute(query)
        daemons_db = result.scalars().all()

        return DaemonFactory.daemons_from_db_model(daemons_db)

    @staticmethod
    def get_daemon_by_account_and_order(
        session: Session, account_id: str, order_id: str
    ) -> Optional[DaemonDomain]:
        query = (
            select(Daemon)
            .join(Order, Daemon.id == Order.daemon_id)
            .where(Order.id == order_id, Daemon.account_id == account_id)
            .limit(1)
        )

        result = session.execute(query)

        daemon_db = result.scalar_one_or_none()
        if daemon_db is None:
            return None

        return DaemonFactory.daemon_from_db_model(daemon_db)

    @staticmethod
    def get_daemon_by_account_and_daemon(
        session: Session, account_id: str, daemon_id: str
    ) -> Optional[DaemonDomain]:
        query = (
            select(Daemon).where(Daemon.id == daemon_id, Daemon.account_id == account_id).limit(1)
        )

        result = session.execute(query)

        daemon_db = result.scalar_one_or_none()
        if daemon_db is None:
            return None

        return DaemonFactory.daemon_from_db_model(daemon_db)
