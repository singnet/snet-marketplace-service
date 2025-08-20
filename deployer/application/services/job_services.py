from deployer.application.schemas.daemon_schemas import DaemonRequest
from deployer.application.schemas.job_schemas import RegistryEventConsumerRequest
from deployer.domain.models.transactions_metadata import TransactionsMetadataDomain
from deployer.exceptions import DaemonNotFoundException
from deployer.infrastructure.clients.deployer_cleint import DeployerClient
from deployer.infrastructure.clients.haas_client import HaaSClient
from deployer.infrastructure.db import session_scope, DefaultSessionFactory
from deployer.infrastructure.models import DaemonStatus, OrderStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository


class ServiceEventConsumer:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self._deployer_client = DeployerClient()

    def on_event(self, request: RegistryEventConsumerRequest):
        event_name = request.event_name
        org_id = request.org_id
        service_id = request.service_id
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.search_daemon(session, org_id, service_id)
            if daemon is None:
                return
            daemon_id = daemon.id

            if event_name == "ServiceDeleted":
                DaemonRepository.update_daemon_service_published(session, daemon_id, False)
                if daemon.status == DaemonStatus.UP:
                    self._deployer_client.stop_daemon(daemon_id)
            elif event_name == "ServiceCreated":
                DaemonRepository.update_daemon_service_published(session, daemon_id, True)
            elif event_name == "ServiceMetadataModified":
                if daemon.status == DaemonStatus.UP:
                    self._deployer_client.redeploy_daemon(daemon_id)


class JobService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self._deployer_client = DeployerClient()
        self._haas_client = HaaSClient()

    def update_transaction_status(self):
        with session_scope(self.session_factory) as session:
            transactions_metadatas = TransactionRepository.get_transactions_metadata(session)
        for transactions_metadata in transactions_metadatas:
            transactions = self._get_transactions_from_blockchain(transactions_metadata)
            for transaction in transactions:
                TransactionRepository.upsert_transaction(session, transaction)
                OrderRepository.update_order_status(session, transaction.order_id, OrderStatus.SUCCESS)
                order = OrderRepository.get_order(session, transaction.order_id)
                DaemonRepository.update_daemon_status(session, order.daemon_id, DaemonStatus.READY_TO_START)

        with session_scope(self.session_factory) as session:
            TransactionRepository.fail_old_transactions(session)
            OrderRepository.fail_old_orders(session)

    def check_daemons(self):
        with session_scope(self.session_factory) as session:
            daemons = DaemonRepository.get_daemons_without_statuses(
                session,
                [DaemonStatus.INIT, DaemonStatus.ERROR, DaemonStatus.DOWN]
            )
        for daemon in daemons:
            if daemon.status == DaemonStatus.READY_TO_START and not daemon.service_published:
                continue

            self._deployer_client.update_daemon_status(daemon.id, asynchronous = True)

    def update_daemon_status(self, request: DaemonRequest):
        daemon_id = request.daemon_id

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)

            if daemon is None:
                raise DaemonNotFoundException(daemon_id)

            haas_daemon_status, started_on = self._haas_client.check_daemon(daemon.org_id, daemon.service_id)

            # TODO: add processing of various daemon statuses

    def _get_transactions_from_blockchain(self, tx_metadata: TransactionsMetadataDomain) -> list:
        pass


