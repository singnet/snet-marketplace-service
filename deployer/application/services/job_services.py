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

    def process_registry_event(self, request: RegistryEventConsumerRequest):
        event_name = request.event_name
        org_id = request.org_id
        service_id = request.service_id
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.search_daemon(session, org_id, service_id)
            if daemon is None:
                logger.info(f"Service (org_id {org_id}, service_id {service_id}) doesn't use HaaS")
                return
            daemon_id = daemon.id

            metadata_uri = request.metadata_uri
            metadata: dict = self._storage_provider.get(metadata_uri)
            try:
                daemon_group = metadata["groups"][0]
                daemon_endpoint = daemon_group["endpoints"][0]
                group_name = daemon_group["group_name"]
                service_api_source = metadata["service_api_source"]
            except KeyError or IndexError:
                logger.exception(
                    f"Failed to get daemon group, endpoint or service api source from metadata: {metadata}",
                    exc_info=True,
                )
                raise Exception(
                    f"Failed to get daemon group, endpoint or service api source from metadata: {metadata}"
                )

            service_class = self._get_service_class(service_api_source)

            if daemon.daemon_endpoint != daemon_endpoint:
                logger.info(f"Service (org_id {org_id}, service_id {service_id}) doesn't use HaaS")
                if daemon.status == DeploymentStatus.UP:
                    logger.info(f"Stopping daemon {daemon_id}")
                    self._deployer_client.stop_daemon(daemon_id)
                return

            new_config = daemon.daemon_config
            new_config["daemon_group"] = group_name
            new_config["service_class"] = service_class

            DaemonRepository.update_daemon_config(session, daemon_id, new_config)

            if event_name == AllowedEventNames.SERVICE_DELETED:
                DaemonRepository.update_daemon_service_published(session, daemon_id, False)
                if daemon.status == DeploymentStatus.UP:
                    self._deployer_client.stop_daemon(daemon_id)
            elif event_name == AllowedEventNames.SERVICE_CREATED:
                DaemonRepository.update_daemon_service_published(session, daemon_id, True)
            elif event_name == AllowedEventNames.SERVICE_METADATA_MODIFIED:
                if daemon.status == DeploymentStatus.UP:
                    self._deployer_client.redeploy_daemon(daemon_id)

    def update_transaction_status(self):
        with session_scope(self.session_factory) as session:
            transactions_metadatas = TransactionRepository.get_transactions_metadata(session)
            for transactions_metadata in transactions_metadatas:
                transactions, last_block = self._get_transactions_from_blockchain(
                    transactions_metadata
                )

                for new_transaction in transactions:
                    existing_transaction = TransactionRepository.get_transaction(
                        session, new_transaction.hash
                    )
                    if not new_transaction.order_id:
                        if existing_transaction is None:
                            raise Exception(
                                f"Transaction {new_transaction.hash} not found in database and has no order id"
                            )
                        new_transaction.order_id = existing_transaction.order_id
                    TransactionRepository.upsert_transaction(session, new_transaction)

                    order = OrderRepository.get_order(session, new_transaction.order_id)
                    OrderRepository.update_order_status(
                        session, new_transaction.order_id, OrderStatus.SUCCESS
                    )

                    daemon = DaemonRepository.get_daemon(session, order.daemon_id)
                    # TODO: find the way to handle the first order with not published service
                    if (
                            daemon.service_published and daemon.status == DeploymentStatus.DOWN
                    ) or not daemon.service_published:
                        DaemonRepository.update_daemon_status(
                            session, order.daemon_id, DeploymentStatus.READY_TO_START
                        )
                        DaemonRepository.update_daemon_end_on(
                            session, order.daemon_id, datetime.now(UTC) + relativedelta(months=+1)
                        )
                    elif daemon.status in [DeploymentStatus.UP, DeploymentStatus.READY_TO_START]:
                        DaemonRepository.update_daemon_end_on(
                            session, order.daemon_id, daemon.end_at + relativedelta(months=+1)
                        )

                    TransactionRepository.update_transactions_metadata(
                        session, transactions_metadata.id, last_block
                    )

            TransactionRepository.fail_old_transactions(session)
            OrderRepository.fail_old_orders(session)

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
                                    session, last_claiming_period.id, ClaimingPeriodStatus.FAILED
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
                                    session, last_claiming_period.id, ClaimingPeriodStatus.FAILED
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

    @staticmethod
    def _get_transactions_from_blockchain(
        tx_metadata: TransactionsMetadataDomain,
    ) -> Tuple[List[NewEVMTransactionDomain], int]:
        blockchain_util = BlockChainUtil("HTTP_PROVIDER", NETWORKS[NETWORK_ID]["http_provider"])
        w3 = blockchain_util.web3_object
        current_block = blockchain_util.get_current_block_no()
        contract = JobService._get_token_contract(blockchain_util)

        from_block = tx_metadata.last_block_no + 1
        to_block = min(
            current_block - tx_metadata.block_adjustment, from_block + tx_metadata.fetch_limit
        )

        transaction_filter = contract.events.Transfer.createFilter(
            fromBlock=from_block, toBlock=to_block, argument_filters={"to": tx_metadata.recipient}
        )

        events = transaction_filter.get_all_entries()
        result = []
        for event in events:
            tx_hash = event["transactionHash"].hex()
            order_id = JobService._get_order_id_from_transaction(tx_hash, w3)
            result.append(
                NewEVMTransactionDomain(
                    hash=tx_hash,
                    order_id=order_id,
                    status=EVMTransactionStatus.SUCCESS,
                    sender=event["args"]["from"],
                    recipient=event["args"]["to"],
                )
            )

        return result, to_block

    @staticmethod
    def _get_token_contract(bc_util: BlockChainUtil):
        base_path = os.path.abspath(
            os.path.join(CONTRACT_BASE_PATH, "node_modules", "singularitynet-token-contracts")
        )

        abi_path = base_path + "/{}/{}".format("abi", TOKEN_JSON_FILE_NAME)
        contract_abi = bc_util.load_contract(abi_path)

        contract_network_path = base_path + "/{}/{}".format("networks", TOKEN_JSON_FILE_NAME)
        contract_network = bc_util.load_contract(contract_network_path)
        contract_address = contract_network[str(NETWORK_ID)]["address"]

        contract_instance = bc_util.contract_instance(
            contract_abi=contract_abi, address=contract_address
        )

        return contract_instance

    @staticmethod
    def _get_order_id_from_transaction(tx_hash: HexStr, w3: Web3) -> str:
        try:
            transaction = w3.eth.get_transaction(tx_hash)
            input_data = transaction["input"]
            input_data_hex = input_data.hex()
            extra_data_hex = input_data_hex[
                136:
            ]  # 8 function signature + 128 transfer tx standard parameters = 136
            if len(extra_data_hex) == 0:
                return ""
            extra_data_bytes = bytes.fromhex(extra_data_hex)
            order_id = extra_data_bytes.decode("utf-8").rstrip("\x00")
            return order_id
        except Exception as e:
            logger.exception(f"Failed to get order id from transaction {tx_hash}: {e}")
            raise e

    def _get_service_class(self, service_api_source: str) -> str:
        tar_bytes = self._storage_provider.get(service_api_source, to_decode=False)
        tar_stream = io.BytesIO(tar_bytes)

        try:
            with tarfile.open(fileobj=tar_stream, mode="r:*") as tar:
                members = [m for m in tar.getmembers() if m.isfile()]

                if not members:
                    raise Exception("No files found in tar archive")

                first_member = members[0]
                file_content = tar.extractfile(first_member)

                if file_content is None:
                    raise Exception("Failed to extract file from tar archive")

                content_text = file_content.read().decode("utf-8")

                for line in content_text.splitlines():
                    line = line.strip()
                    if line.startswith("package ") and line.endswith(";"):
                        package_line = line
                        package_name = package_line.replace("package ", "").replace(";", "").strip()
                        return package_name

        except (tarfile.TarError, IOError, UnicodeDecodeError, Exception) as e:
            raise Exception(f"Error processing tar file: {e}")
