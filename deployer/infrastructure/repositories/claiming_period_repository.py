from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from deployer.constant import CLAIMING_PERIOD
from deployer.domain.factory.claiming_period_factory import ClaimingPeriodFactory
from deployer.domain.models.claiming_period import ClaimingPeriodDomain
from deployer.infrastructure.models import ClaimingPeriod, ClaimingPeriodStatus


class ClaimingPeriodRepository:
    @staticmethod
    def create_claiming_period(session: Session, daemon_id: str) -> None:
        current_time = datetime.now(UTC)
        claiming_period_model = ClaimingPeriod(
            daemon_id = daemon_id,
            start_on = current_time,
            end_on = current_time + CLAIMING_PERIOD,
            status = ClaimingPeriodStatus.ACTIVE
        )

        session.add(claiming_period_model)

    @staticmethod
    def get_last_claiming_period(session: Session, daemon_id: str) -> Optional[ClaimingPeriodDomain]:
        query = select(
            ClaimingPeriod
        ).where(
            ClaimingPeriod.daemon_id == daemon_id
        ).order_by(
            ClaimingPeriod.end_on.desc()
        ).limit(1)

        result = session.execute(query)

        claiming_period_db = result.scalar_one_or_none()
        if claiming_period_db is None:
            return None

        return ClaimingPeriodFactory.claiming_period_from_db_model(
            claiming_period_db
        )

    @staticmethod
    def update_claiming_period_status(session: Session, claiming_period_id: int, status: ClaimingPeriodStatus) -> None:
        query = update(
            ClaimingPeriod
        ).where(
            ClaimingPeriod.id == claiming_period_id
        ).values(
            status=status
        )

        session.execute(query)
