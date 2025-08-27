from typing import Iterable, List

from deployer.domain.models.claiming_period import ClaimingPeriodDomain
from deployer.infrastructure.models import ClaimingPeriod


class ClaimingPeriodFactory:
    @staticmethod
    def claiming_period_from_db_model(
        claiming_period_db_model: ClaimingPeriod,
    ) -> ClaimingPeriodDomain:
        return ClaimingPeriodDomain(
            id=claiming_period_db_model.id,
            daemon_id=claiming_period_db_model.daemon_id,
            start_at=claiming_period_db_model.start_at,
            end_at=claiming_period_db_model.end_at,
            status=claiming_period_db_model.status,
            created_at=claiming_period_db_model.created_at,
            updated_at=claiming_period_db_model.updated_at,
        )

    @staticmethod
    def claiming_period_from_db_models(
        claiming_period_db_models: Iterable[ClaimingPeriod],
    ) -> List[ClaimingPeriodDomain]:
        return [
            ClaimingPeriodFactory.claiming_period_from_db_model(claiming_period_db_model)
            for claiming_period_db_model in claiming_period_db_models
        ]
