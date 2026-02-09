from typing import Optional

from common.exceptions import ForbiddenException
from common.request_context import RequestContext
from deployer.infrastructure.clients.registry_client import RegistryClient
from deployer.infrastructure.db import session_scope, DefaultSessionFactory
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.hosted_service_repository import HostedServiceRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository


class AuthorizationService:
    def __init__(self, session_factory=None, registry_client=None):
        self.session_factory = DefaultSessionFactory if session_factory is None else session_factory
        self._registry_client = RegistryClient() if registry_client is None else registry_client

    def check_local_access(
        self,
        account_id: str,
        daemon_id: Optional[str] = None,
        order_id: Optional[str] = None,
        hosted_service_id: Optional[str] = None,
    ):
        optional_params = [daemon_id, order_id, hosted_service_id]
        optional_params_count = sum(1 for param in optional_params if param is not None)

        if optional_params_count != 1:
            raise ValueError(
                "Exactly one of daemon_id, order_id or hosted_service_id must be provided"
            )

        with session_scope(self.session_factory) as session:
            if daemon_id is not None:
                entity = DaemonRepository.get_daemon_by_account_and_daemon(
                    session, account_id, daemon_id
                )
            elif order_id is not None:
                entity = OrderRepository.get_order(
                    session, account_id=account_id, order_id=order_id
                )
            else:
                entity = HostedServiceRepository.get_hosted_service_by_account_and_service(
                    session, account_id, hosted_service_id
                )

        if entity is None:
            raise ForbiddenException()

    def check_service_access(self, request_context: RequestContext, org_id: str):
        orgs = self._registry_client.get_all_orgs(
            request_context.username, request_context.account_id, request_context.origin
        )

        is_accessed = False

        for org in orgs:
            if org["org_id"] == org_id:
                is_accessed = True
                break

        if not is_accessed:
            raise ForbiddenException()
