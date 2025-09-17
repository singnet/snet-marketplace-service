from typing import Optional

from common.exceptions import ForbiddenException
from common.request_context import RequestContext
from deployer.infrastructure.clients.registry_client import RegistryClient
from deployer.infrastructure.db import session_scope, DefaultSessionFactory
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository


class AuthorizationService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self._registry_client = RegistryClient()

    def check_local_access(
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

    def check_service_access(self, request_context: RequestContext, org_id: str):
        orgs = self._registry_client.get_all_orgs(
            request_context.username,
            request_context.account_id,
            request_context.origin
        )

        is_accessed = False

        for org in orgs:
            if org["org_id"] == org_id:
                is_accessed = True
                break

        if not is_accessed:
            raise ForbiddenException()