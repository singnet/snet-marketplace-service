import os
from datetime import datetime, UTC, timedelta

from eth_typing import HexStr
from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from deployer.application.schemas.daemon_schemas import DaemonRequest
from deployer.application.schemas.job_schemas import RegistryEventConsumerRequest
from deployer.config import (
    NETWORKS,
    NETWORK_ID,
    CONTRACT_BASE_PATH,
    TOKEN_JSON_FILE_NAME,
    TRANSFER_TARGET_ADDRESS, DAEMON_STARTING_TTL_IN_MINUTES, DAEMON_RESTARTING_TTL_IN_MINUTES
)
from deployer.domain.models.evm_transaction import NewEVMTransactionDomain
from deployer.domain.models.transactions_metadata import TransactionsMetadataDomain
from deployer.exceptions import DaemonNotFoundException
from deployer.infrastructure.clients.deployer_cleint import DeployerClient
from deployer.infrastructure.clients.haas_client import HaaSClient, HaaSDaemonStatus
from deployer.infrastructure.db import session_scope, DefaultSessionFactory
from deployer.infrastructure.models import DaemonStatus, OrderStatus, EVMTransactionStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository


logger = get_logger(__name__)


class JobService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self._deployer_client = DeployerClient()
        self._haas_client = HaaSClient()

    def process_registry_event(self, request: RegistryEventConsumerRequest):
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

    def update_transaction_status(self):
        with session_scope(self.session_factory) as session:
            transactions_metadatas = TransactionRepository.get_transactions_metadata(session)
            for transactions_metadata in transactions_metadatas:
                transactions, last_block = self._get_transactions_from_blockchain(transactions_metadata)

                for new_transaction in transactions:
                    existing_transaction = TransactionRepository.get_transaction(session, new_transaction.hash)
                    if not new_transaction.order_id:
                        if existing_transaction is None:
                            raise Exception(f"Transaction {new_transaction.hash} not found in database and has no order id")
                        new_transaction.order_id = existing_transaction.order_id
                    TransactionRepository.upsert_transaction(session, new_transaction)

                    order = OrderRepository.get_order(session, new_transaction.order_id)
                    OrderRepository.update_order_status(session, new_transaction.order_id, OrderStatus.SUCCESS)
                    DaemonRepository.update_daemon_status(session, order.daemon_id, DaemonStatus.READY_TO_START)

                    TransactionRepository.update_transactions_metadata(session, transactions_metadata.id, last_block)

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
            daemon_status = daemon.status
            service_published = daemon.service_published

            if daemon is None:
                raise DaemonNotFoundException(daemon_id)

            haas_daemon_status, started_on = self._haas_client.check_daemon(daemon.org_id, daemon.service_id)
            last_order = OrderRepository.get_last_order(session, daemon_id)

            current_time = datetime.now(UTC)
            if service_published:
                if haas_daemon_status == HaaSDaemonStatus.DOWN:
                    if daemon_status == DaemonStatus.READY_TO_START:
                        self._deployer_client.start_daemon(daemon_id)
                    elif daemon_status == DaemonStatus.STARTING:
                        if daemon.updated_on + timedelta(minutes = DAEMON_STARTING_TTL_IN_MINUTES) < current_time:
                            DaemonRepository.update_daemon_status(session, daemon_id, DaemonStatus.ERROR)
                    elif daemon_status == DaemonStatus.UP or DaemonStatus.DELETING:
                        DaemonRepository.update_daemon_status(session, daemon_id, DaemonStatus.DOWN)
                    elif daemon_status == DaemonStatus.RESTARTING:
                        if daemon.updated_on + timedelta(minutes = DAEMON_RESTARTING_TTL_IN_MINUTES) < current_time:
                            DaemonRepository.update_daemon_status(session, daemon_id, DaemonStatus.ERROR)
                else:






    @staticmethod
    def _get_transactions_from_blockchain(tx_metadata: TransactionsMetadataDomain) -> tuple[list[NewEVMTransactionDomain], int]:
        blockchain_util = BlockChainUtil("HTTP_PROVIDER", NETWORKS[NETWORK_ID]['http_provider'])
        w3 = blockchain_util.web3_object
        current_block = blockchain_util.get_current_block_no()
        contract = JobService._get_token_contract(blockchain_util)

        from_block = tx_metadata.last_block_no + 1
        to_block = min(current_block - tx_metadata.block_adjustment, from_block + tx_metadata.fetch_limit)

        transaction_filter = contract.events.Transfer.createFilter(
            fromBlock=from_block,
            toBlock=to_block,
            argument_filters = {'to': TRANSFER_TARGET_ADDRESS}
        )

        events = transaction_filter.get_all_entries()
        result = []
        for event in events:
            tx_hash = event['transactionHash'].hex()
            order_id = JobService._get_order_id_from_transaction(tx_hash, w3)
            result.append(
                NewEVMTransactionDomain(
                    hash=tx_hash,
                    order_id=order_id,
                    status=EVMTransactionStatus.SUCCESS,
                    sender=event['args']['from'],
                    recipient=event['args']['to']
                )
            )

        return result, to_block

    @staticmethod
    def _get_token_contract(bc_util: BlockChainUtil):
        base_path = os.path.abspath(
            os.path.join(CONTRACT_BASE_PATH, 'node_modules', 'singularitynet-token-contracts'))

        abi_path = base_path + "/{}/{}".format("abi", TOKEN_JSON_FILE_NAME)
        contract_abi = bc_util.load_contract(abi_path)

        contract_network_path = base_path + "/{}/{}".format("networks", TOKEN_JSON_FILE_NAME)
        contract_network = bc_util.load_contract(contract_network_path)
        contract_address = contract_network[str(NETWORK_ID)]['address']

        contract_instance = bc_util.contract_instance(contract_abi=contract_abi, address=contract_address)

        return contract_instance

    @staticmethod
    def _get_order_id_from_transaction(tx_hash: HexStr, w3: Web3) -> str:
        try:
            transaction = w3.eth.get_transaction(tx_hash)
            input_data = transaction['input']
            input_data_hex = input_data.hex()
            extra_data_hex = input_data_hex[136:] # 8 function signature + 128 transfer tx standard parameters = 136
            if len(extra_data_hex) == 0:
                return ""
            extra_data_bytes = bytes.fromhex(extra_data_hex)
            order_id = extra_data_bytes.decode('utf-8').rstrip('\x00')
            return order_id
        except Exception as e:
            logger.exception(f"Failed to get order id from transaction {tx_hash}: {e}")
            raise e










