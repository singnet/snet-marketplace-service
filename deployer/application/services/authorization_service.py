from typing import Optional

from common.exceptions import ForbiddenException
from deployer.infrastructure.db import session_scope, DefaultSessionFactory
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository


class AuthorizationService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory

    def check_access(
        self, account_id: str, daemon_id: Optional[str] = None, order_id: Optional[str] = None
    ):
        account_id = account_id
        with session_scope(self.session_factory) as session:
            if daemon_id is not None:
                daemon = DaemonRepository().get_daemon_by_account_and_daemon(
                    session, account_id, daemon_id
                )
            else:
                daemon = DaemonRepository().get_daemon_by_account_and_order(
                    session, account_id, order_id
                )

        if daemon is None:
            raise ForbiddenException()
