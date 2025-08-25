from typing import Iterable, List

from deployer.domain.models.daemon import DaemonDomain
from deployer.infrastructure.models import Daemon


class DaemonFactory:
    @staticmethod
    def daemon_from_db_model(daemon_db_model: Daemon) -> DaemonDomain:
        return DaemonDomain(
            id=daemon_db_model.id,
            account_id=daemon_db_model.account_id,
            org_id=daemon_db_model.org_id,
            service_id=daemon_db_model.service_id,
            status=daemon_db_model.status,
            daemon_config=daemon_db_model.daemon_config,
            start_on=daemon_db_model.start_on,
            end_on=daemon_db_model.end_on,
            service_published=daemon_db_model.service_published,
            daemon_endpoint=daemon_db_model.daemon_endpoint,
            created_at=daemon_db_model.created_at,
            updated_at=daemon_db_model.updated_at,
        )

    @staticmethod
    def daemons_from_db_model(daemons_db_model: Iterable[Daemon]) -> List[DaemonDomain]:
        return [
            DaemonFactory.daemon_from_db_model(daemon_db_model)
            for daemon_db_model in daemons_db_model
        ]
