from datetime import datetime, UTC, timedelta
from typing import Optional, List, Dict

from sqlalchemy import select, update, func, and_
from sqlalchemy.orm import Session

from deployer.config import CLAIMING_PERIOD_IN_HOURS
from deployer.domain.factory.claiming_period_factory import ClaimingPeriodFactory
from deployer.domain.models.claiming_period import ClaimingPeriodDomain
from deployer.infrastructure.models import ClaimingPeriod, ClaimingPeriodStatus


class ClaimingPeriodRepository:
    @staticmethod
    def create_claiming_period(session: Session, daemon_id: str) -> None:
        current_time = datetime.now(UTC)
        claiming_period_model = ClaimingPeriod(
            daemon_id=daemon_id,
            start_at=current_time,
            end_at=current_time + timedelta(hours=CLAIMING_PERIOD_IN_HOURS),
            status=ClaimingPeriodStatus.ACTIVE,
        )

        session.add(claiming_period_model)

    @staticmethod
    def get_last_claiming_period(
        session: Session, daemon_id: str
    ) -> Optional[ClaimingPeriodDomain]:
        query = (
            select(ClaimingPeriod)
            .where(ClaimingPeriod.daemon_id == daemon_id)
            .order_by(ClaimingPeriod.end_at.desc())
            .limit(1)
        )

        result = session.execute(query)

        claiming_period_db = result.scalar_one_or_none()
        if claiming_period_db is None:
            return None

        return ClaimingPeriodFactory.claiming_period_from_db_model(claiming_period_db)

    @staticmethod
    def get_last_claiming_periods_batch(
        session: Session, daemon_ids: List[str]
    ) -> Dict[str, ClaimingPeriodDomain]:
        if not daemon_ids:
            return {}

        subquery = (
            select(ClaimingPeriod.daemon_id, func.max(ClaimingPeriod.end_at).label("max_end_at"))
            .where(ClaimingPeriod.daemon_id.in_(daemon_ids))
            .group_by(ClaimingPeriod.daemon_id)
            .subquery()
        )

        query = select(ClaimingPeriod).join(
            subquery,
            and_(
                ClaimingPeriod.daemon_id == subquery.c.daemon_id,
                ClaimingPeriod.end_at == subquery.c.max_end_at,
            ),
        )

        result = session.execute(query)
        claiming_periods_db = result.scalars().all()

        claiming_periods = {}
        for claiming_period_db in claiming_periods_db:
            claiming_period = ClaimingPeriodFactory.claiming_period_from_db_model(
                claiming_period_db
            )
            claiming_periods[claiming_period.daemon_id] = claiming_period

        return claiming_periods

    @staticmethod
    def update_claiming_period_status(
        session: Session, claiming_period_id: int, status: ClaimingPeriodStatus
    ) -> None:
        query = (
            update(ClaimingPeriod)
            .where(ClaimingPeriod.id == claiming_period_id)
            .values(status=status)
        )

        session.execute(query)
