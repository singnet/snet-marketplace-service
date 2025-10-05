import io
import os
import tarfile
from datetime import datetime, UTC, timedelta
from typing import List, Tuple

from dateutil.relativedelta import relativedelta

from eth_typing import HexStr
from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from common.storage_provider import StorageProvider
from deployer.application.schemas.daemon_schemas import DaemonRequest
from deployer.application.schemas.job_schemas import RegistryEventConsumerRequest
from deployer.config import (
    NETWORKS,
    NETWORK_ID,
    CONTRACT_BASE_PATH,
    TOKEN_JSON_FILE_NAME,
    DAEMON_STARTING_TTL_IN_MINUTES,
    DAEMON_RESTARTING_TTL_IN_MINUTES,
)
from deployer.constant import AllowedEventNames
from deployer.domain.models.evm_transaction import NewEVMTransactionDomain
from deployer.domain.models.transactions_metadata import TransactionsMetadataDomain
from deployer.exceptions import DaemonNotFoundException
from deployer.infrastructure.clients.deployer_cleint import DeployerClient
from deployer.infrastructure.clients.haas_client import HaaSClient, HaaSDaemonStatus
from deployer.infrastructure.db import session_scope, DefaultSessionFactory
from deployer.infrastructure.models import (
    DeploymentStatus,
    OrderStatus,
    EVMTransactionStatus,
    ClaimingPeriodStatus,
)
from deployer.infrastructure.repositories.claiming_period_repository import ClaimingPeriodRepository
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository


logger = get_logger(__name__)


class JobService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self._deployer_client = DeployerClient()
        self._haas_client = HaaSClient()
        self._storage_provider = StorageProvider()

    def check_daemons(self):
        with session_scope(self.session_factory) as session:
            daemons = DaemonRepository.get_daemons_without_statuses(
                session, [DeploymentStatus.INIT, DeploymentStatus.ERROR, DeploymentStatus.DOWN]
            )
            logger.info(f"Found {len(daemons)} daemons to check")
        for daemon in daemons:
            if daemon.status == DeploymentStatus.READY_TO_START and not daemon.service_published:
                continue

            self._deployer_client.update_daemon_status(daemon.id, asynchronous=True)

    def update_daemon_status(self, request: DaemonRequest):
        daemon_id = request.daemon_id

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)
            daemon_status = daemon.status
            service_published = daemon.service_published

            if daemon is None:
                raise DaemonNotFoundException(daemon_id)

            haas_daemon_status, started_on = self._haas_client.check_daemon(
                daemon.org_id, daemon.service_id
            )
            last_claiming_period = ClaimingPeriodRepository.get_last_claiming_period(
                session, daemon_id
            )
            current_time = datetime.now(UTC)

            if (
                last_claiming_period
                and last_claiming_period.status == ClaimingPeriodStatus.ACTIVE
                and last_claiming_period.end_at < current_time
            ):
                ClaimingPeriodRepository.update_claiming_period_status(
                    session, last_claiming_period.id, ClaimingPeriodStatus.INACTIVE
                )

            logger.info(
                f"Daemon {daemon_id}, status: {daemon_status}, HaaS status: {haas_daemon_status}, "
                f"service published: {service_published}, updated on: {daemon.updated_at}, "
                f"last claiming period: {last_claiming_period.to_response() if last_claiming_period else None}"
            )

            if service_published:
                if haas_daemon_status == HaaSDaemonStatus.DOWN:
                    if daemon_status == DeploymentStatus.READY_TO_START:
                        self._deployer_client.start_daemon(daemon_id)
                    elif daemon_status == DeploymentStatus.STARTING:
                        if (
                            daemon.updated_at.replace(tzinfo = UTC) + timedelta(minutes=DAEMON_STARTING_TTL_IN_MINUTES)
                            < current_time
                        ):
                            DaemonRepository.update_daemon_status(
                                session, daemon_id, DeploymentStatus.ERROR
                            )
                            if (
                                last_claiming_period
                                and last_claiming_period.status == ClaimingPeriodStatus.ACTIVE
                            ):
                                ClaimingPeriodRepository.update_claiming_period_status(
                                    session, last_claiming_period.id, ClaimingPeriodStatus.PAYMENT_FAILED
                                )
                    elif daemon_status == DeploymentStatus.UP or DeploymentStatus.DELETING:
                        DaemonRepository.update_daemon_status(session, daemon_id, DeploymentStatus.DOWN)
                    elif daemon_status == DeploymentStatus.RESTARTING:
                        if (
                            daemon.updated_at.replace(tzinfo = UTC) + timedelta(minutes=DAEMON_RESTARTING_TTL_IN_MINUTES)
                            < current_time
                        ):
                            DaemonRepository.update_daemon_status(
                                session, daemon_id, DeploymentStatus.ERROR
                            )
                            if (
                                last_claiming_period
                                and last_claiming_period.status == ClaimingPeriodStatus.ACTIVE
                            ):
                                ClaimingPeriodRepository.update_claiming_period_status(
                                    session, last_claiming_period.id, ClaimingPeriodStatus.PAYMENT_FAILED
                                )
                elif haas_daemon_status == HaaSDaemonStatus.UP:
                    if (
                        daemon_status == DeploymentStatus.STARTING
                        or daemon_status == DeploymentStatus.RESTARTING
                    ):
                        DaemonRepository.update_daemon_status(session, daemon_id, DeploymentStatus.UP)
                    elif daemon_status == DeploymentStatus.UP:
                        if daemon.end_at < current_time:
                            if (
                                last_claiming_period
                                and last_claiming_period.status != ClaimingPeriodStatus.ACTIVE
                            ):
                                self._deployer_client.stop_daemon(daemon_id)




