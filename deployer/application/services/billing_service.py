from common.utils import generate_uuid
from deployer.application.schemas.billing_schemas import CreateOrderRequest, SaveEVMTransactionRequest
from deployer.domain.models.evm_transaction import NewEVMTransactionDomain
from deployer.domain.models.order import NewOrderDomain
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.models import OrderStatus, EVMTransactionStatus
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository


class BillingService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory

    def create_order(self, request: CreateOrderRequest, account_id: str):
        order_id = generate_uuid()

        with session_scope(self.session_factory) as session:
            order = OrderRepository.get_order(
                session=session, account_id=account_id, status = OrderStatus.INIT
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
                        status=OrderStatus.INIT,
                    ),
                )

        return {"orderId": order_id}

    def save_evm_transaction(self, request: SaveEVMTransactionRequest):
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

    def get_balance(self):
        pass

    def get_balance_history(self):
        pass

    def get_metrics(self):
        pass

    def update_transaction_status(self):
        pass

    def process_call_event(self):
        pass
