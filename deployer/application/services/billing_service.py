import os
from typing import Tuple, List

import requests
from eth_typing import HexStr
from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from common.utils import generate_uuid
from deployer.application.schemas.billing_schemas import (
    CreateOrderRequest,
    SaveEVMTransactionRequest,
    GetBalanceHistoryRequest,
    CallEventConsumerRequest,
    GetBalanceAndRateRequest,
)
from deployer.config import (
    NETWORKS,
    NETWORK_ID,
    CONTRACT_BASE_PATH,
    TOKEN_JSON_FILE_NAME,
    TOKEN_NAME,
    TOKEN_DECIMALS,
)
from deployer.constant import TypeOfMovementOfFunds, OrderType, IncomeStatus
from deployer.domain.models.account_balance import NewAccountBalanceDomain
from deployer.domain.models.evm_transaction import NewEVMTransactionDomain
from deployer.domain.models.order import NewOrderDomain
from deployer.domain.models.token_rate import NewTokenRateDomain
from deployer.domain.models.transactions_metadata import TransactionsMetadataDomain
from deployer.exceptions import (
    OrderNotFoundException,
    UnacceptableOrderStatusException,
    HostedServiceNotFoundException,
)
from deployer.infrastructure.clients.haas_client import HaaSClient
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.models import OrderStatus, EVMTransactionStatus
from deployer.infrastructure.repositories.account_balance_repository import AccountBalanceRepository
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.infrastructure.repositories.token_rate_repository import TokenRateRepository
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository


logger = get_logger(__name__)


class BillingService:
    def __init__(self, session_factory=None):
        self.session_factory = DefaultSessionFactory
        self._haas_client = HaaSClient()

    def create_order(self, request: CreateOrderRequest, account_id: str) -> dict:
        with session_scope(self.session_factory) as session:
            order = OrderRepository.get_order(
                session=session, account_id=account_id, status=OrderStatus.CREATED
            )

            if order is not None and order.amount == request.amount:
                logger.info("Order already exists")
                order_id = order.id
            else:
                if order is not None:
                    OrderRepository.update_order_status(
                        session=session,
                        order_id=order.id,
                        status=OrderStatus.CANCELLED,
                    )

                account_balance = AccountBalanceRepository.get_account_balance(
                    session=session, account_id=account_id
                )
                if account_balance is None:
                    AccountBalanceRepository.upsert_account_balance(
                        session=session,
                        account_balance=NewAccountBalanceDomain(
                            account_id=account_id, balance_in_cogs=0
                        ),
                    )

                order_id = generate_uuid()
                OrderRepository.create_order(
                    session=session,
                    order=NewOrderDomain(
                        id=order_id,
                        account_id=account_id,
                        amount=request.amount,
                        status=OrderStatus.CREATED,
                    ),
                )

        return {"orderId": order_id}

    def save_evm_transaction(self, request: SaveEVMTransactionRequest) -> dict:
        with session_scope(self.session_factory) as session:
            TransactionRepository.upsert_transaction(
                session,
                NewEVMTransactionDomain(
                    hash=request.transaction_hash,
                    order_id=request.order_id,
                    status=EVMTransactionStatus.PENDING,
                    sender=request.sender,
                    recipient=request.recipient,
                ),
            )

            order = OrderRepository.get_order(session, request.order_id)

            if order is None:
                logger.exception(
                    f"Order with id {request.order_id} for transaction {request.transaction_hash} not found"
                )
                raise OrderNotFoundException(request.order_id)

            if order.status not in [OrderStatus.CREATED, OrderStatus.FAILED]:
                logger.exception(
                    f"Order with id {request.order_id} must have the status CREATED or PAYMENT_FAILED for "
                    f"correct saving of transaction {request.transaction_hash}"
                )
                raise UnacceptableOrderStatusException(order.status.value)

            OrderRepository.update_order_status(
                session=session,
                order_id=request.order_id,
                status=OrderStatus.PROCESSING,
            )

        return {}

    def get_balance(self, account_id: str) -> dict:
        balance = 0
        with session_scope(self.session_factory) as session:
            account_balance = AccountBalanceRepository.get_account_balance(session, account_id)

            if account_balance is not None:
                balance = int(account_balance.balance_in_cogs)

        return {"balanceInCogs": balance}

    def get_balance_and_rate(self, request: GetBalanceAndRateRequest) -> dict:
        balance = 0
        with session_scope(self.session_factory) as session:
            account_balance = AccountBalanceRepository.get_account_balance_by_service(
                session, request.org_id, request.service_id
            )

            if account_balance is not None:
                balance = int(account_balance.balance_in_cogs)

            average_cogs_per_usd = TokenRateRepository.get_average_cogs_per_usd(session, TOKEN_NAME)

        return {"balanceInCogs": balance, "cogsPerUsd": average_cogs_per_usd}

    def get_balance_history(self, request: GetBalanceHistoryRequest, account_id: str) -> dict:
        balance_events = []
        total_count = 0

        if request.type_of_movement != TypeOfMovementOfFunds.INCOME:
            with session_scope(self.session_factory) as session:
                daemons = DaemonRepository.get_user_daemons(session, account_id)
            response = self._haas_client.get_call_events(
                limit=request.limit,
                page=request.page,
                order=request.order,
                period=request.period,
                services=[(daemon.org_id, daemon.service_id) for daemon in daemons],
            )
            for call_event in response.events:
                balance_events.append(
                    {
                        "type": TypeOfMovementOfFunds.EXPENSE.value,
                        "eventName": "Service Call",
                        "amount": call_event.amount,
                        "timestamp": call_event.timestamp.isoformat(),
                    }
                )
            total_count += response.total_count

        status_filter = request.income_status.value
        if status_filter == IncomeStatus.ALL.value:
            status_filter = None
        elif status_filter == IncomeStatus.PENDING.value:
            status_filter = OrderStatus.PROCESSING.value

        if request.type_of_movement != TypeOfMovementOfFunds.EXPENSE:
            with session_scope(self.session_factory) as session:
                top_up_events = OrderRepository.get_orders(
                    session,
                    account_id,
                    request.limit,
                    request.page,
                    request.order,
                    request.period,
                    status_filter,
                )
                top_up_events_total_count = OrderRepository.get_orders_total_count(
                    session, account_id, request.period, OrderStatus.SUCCESS
                )
            for top_up_event in top_up_events:
                balance_events.append(
                    {
                        "type": TypeOfMovementOfFunds.INCOME.value,
                        "eventName": "Top Up",
                        "amount": int(top_up_event.amount),
                        "timestamp": top_up_event.updated_at.isoformat(),
                        "evmTransactions": top_up_event.to_response()["evmTransactions"],
                    }
                )
            total_count += top_up_events_total_count

        if request.type_of_movement == TypeOfMovementOfFunds.ALL:
            balance_events.sort(
                key=lambda x: x["timestamp"], reverse=(request.order == OrderType.DESC)
            )

            if len(balance_events) > request.limit:
                balance_events = balance_events[: request.limit]

        return {"events": balance_events, "totalCount": total_count}

    def update_transaction_status(self):
        with session_scope(self.session_factory) as session:
            transactions_metadata_list = TransactionRepository.get_transactions_metadata(session)
            for transactions_metadata in transactions_metadata_list:
                transactions, last_block = self._get_transactions_from_blockchain(
                    transactions_metadata
                )
                logger.info(
                    f"Found {len(transactions)} new transactions for recipient {transactions_metadata.recipient}"
                )

                for new_transaction, amount in transactions:
                    existing_transaction = TransactionRepository.get_transaction(
                        session, new_transaction.hash
                    )
                    if not new_transaction.order_id:
                        if existing_transaction is None:
                            logger.exception(
                                f"Transaction {new_transaction.hash} not found in database and has no order id",
                                exc_info=True,
                            )
                            continue
                        new_transaction.order_id = existing_transaction.order_id

                    TransactionRepository.upsert_transaction(session, new_transaction)

                    order = OrderRepository.get_order(session, new_transaction.order_id)

                    if order.amount != amount:
                        logger.exception(
                            f"Transaction {new_transaction.hash} has different amount {amount} than "
                            f"order {order.amount}"
                        )
                        continue

                    if order.status != OrderStatus.PROCESSING:
                        logger.exception(
                            f"Order with id {new_transaction.order_id} must have the status PROCESSING for "
                            f"correct processing of transaction {new_transaction.hash}"
                        )
                        continue

                    OrderRepository.update_order_status(session, order.id, OrderStatus.SUCCESS)
                    AccountBalanceRepository.increase_account_balance(
                        session, order.account_id, order.amount
                    )
                TransactionRepository.update_transactions_metadata(
                    session, transactions_metadata.id, last_block
                )

            TransactionRepository.fail_old_transactions(session)
            OrderRepository.fail_old_orders(session)
            OrderRepository.expire_old_orders(session)

    def process_call_event(self, request: CallEventConsumerRequest):
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.search_daemon(session, request.org_id, request.service_id)

            if daemon is None or daemon.hosted_service is None:
                raise HostedServiceNotFoundException(
                    org_id=request.org_id, service_id=request.service_id
                )

            AccountBalanceRepository.decrease_account_balance(
                session, daemon.account_id, request.amount
            )

    def update_token_rate(self) -> None:
        url = "https://api.coingecko.com/api/v3/simple/price"
        token_symbol = TOKEN_NAME.lower()

        query_params = {"symbols": token_symbol, "vs_currencies": "usd"}

        response = requests.get(url, params=query_params)

        token_rate = float(response.json()[token_symbol]["usd"])
        cogs_per_usd = round(10**TOKEN_DECIMALS / token_rate)

        with session_scope(self.session_factory) as session:
            TokenRateRepository.add_token_rate(
                session,
                NewTokenRateDomain(
                    token_symbol=token_symbol, usd_per_token=token_rate, cogs_per_usd=cogs_per_usd
                ),
            )
            TokenRateRepository.delete_old_token_rates(session)

    @staticmethod
    def _get_transactions_from_blockchain(
        tx_metadata: TransactionsMetadataDomain,
    ) -> Tuple[List[Tuple[NewEVMTransactionDomain, int]], int]:
        logger.info(f"Transactions metadata: {tx_metadata.to_response()}")
        blockchain_util = BlockChainUtil("HTTP_PROVIDER", NETWORKS[NETWORK_ID]["http_provider"])
        w3 = blockchain_util.web3_object
        current_block = blockchain_util.get_current_block_no()
        logger.info(f"Current block: {current_block}")
        contract = BillingService._get_token_contract(blockchain_util)

        from_block = tx_metadata.last_block_no + 1
        to_block = min(
            current_block - tx_metadata.block_adjustment, from_block + tx_metadata.fetch_limit
        )
        logger.info(f"Fetching transactions from {from_block} to {to_block}")

        transaction_filter = contract.events.Transfer.create_filter(
            from_block=from_block, to_block=to_block, argument_filters={"to": tx_metadata.recipient}
        )

        events = transaction_filter.get_all_entries()
        result = []
        for event in events:
            logger.info(f"Processing transaction {event['transactionHash'].hex()}")
            tx_hash = event["transactionHash"].hex()
            order_id = BillingService._get_order_id_from_transaction(tx_hash, w3)
            logger.info(f"Order id: {order_id}")
            result.append(
                (
                    NewEVMTransactionDomain(
                        hash=tx_hash if tx_hash.startswith("0x") else "0x" + tx_hash,
                        order_id=order_id,
                        status=EVMTransactionStatus.SUCCESS,
                        sender=event["args"]["from"],
                        recipient=event["args"]["to"],
                    ),
                    event["args"]["value"],
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
