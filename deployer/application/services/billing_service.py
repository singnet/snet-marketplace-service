from common.utils import generate_uuid
from deployer.application.schemas.billing_schemas import CreateOrderRequest, SaveEVMTransactionRequest, \
    GetBalanceHistoryRequest
from deployer.constant import TypeOfMovementOfFunds
from deployer.domain.models.evm_transaction import NewEVMTransactionDomain
from deployer.domain.models.order import NewOrderDomain
from deployer.infrastructure.clients.haas_client import HaaSClient
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.models import OrderStatus, EVMTransactionStatus
from deployer.infrastructure.repositories.account_balance_repository import AccountBalanceRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository


class BillingService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self._haas_client = HaaSClient()

    def create_order(self, request: CreateOrderRequest, account_id: str) -> dict:
        order_id = generate_uuid()

        with session_scope(self.session_factory) as session:
            order = OrderRepository.get_order(
                session=session, account_id=account_id, status = OrderStatus.CREATED
            )

            if order is not None and order.amount == request.amount:
                order_id = order.id
            else:
                if order is not None:
                    OrderRepository.update_order_status(
                        session=session,
                        order_id=order.id,
                        status=OrderStatus.CANCELLED,
                    )

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
                    hash = request.transaction_hash,
                    order_id = request.order_id,
                    status = EVMTransactionStatus.PENDING,
                    sender = request.sender,
                    recipient = request.recipient,
                ),
            )

        return {}

    def get_balance(self, account_id: str) -> dict:
        balance = 0
        with session_scope(self.session_factory) as session:
            account_balance = AccountBalanceRepository.get_account_balance(session, account_id)

            if account_balance is not None:
                balance = account_balance.balance_in_cogs

        return {"balanceInCogs": balance}

    def get_balance_history(self, request: GetBalanceHistoryRequest, account_id: str) -> dict:
        call_events = []

        if request.type_of_movement != TypeOfMovementOfFunds.INCOME:
            call_events = self._haas_client.get_call_events(request.limit, request.page, request.order, request.period)




    def get_metrics(self):
        pass

    def update_transaction_status(self):
        pass

    def process_call_event(self):
        pass
