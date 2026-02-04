from deployer.application.handlers.billing_handlers import create_order, save_evm_transaction, get_balance
from deployer.domain.models.order import NewOrderDomain
from deployer.infrastructure.db import session_scope
from deployer.infrastructure.models import OrderStatus, EVMTransactionStatus
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.tests.functional.utils import validate_response_ok, generate_request_event


class TestBillingEndpoints:
    def test_create_order_ok(self, test_billing_service, test_session_factory):
        order_amount = 123
        event = generate_request_event(body={"amount": order_amount})

        response = create_order(event, None, billing_service=test_billing_service)

        status, data = validate_response_ok(response)
        response_order_id = data.get("orderId")
        assert response_order_id is not None and response_order_id != "", (
            f"No ORDER ID in the response! Response data: {data}"
        )

        with session_scope(test_session_factory) as session:
            order = OrderRepository.get_order(session, response_order_id)

        assert order is not None, "Order has not been created!"
        assert order.amount == order_amount

    def test_save_evm_transaction_ok(
        self,
        test_billing_service,
        test_auth_service,
        test_session_factory,
        add_test_account_balance,
        test_account_id,
    ):
        order_amount = 123
        order_id = "123"

        with session_scope(test_session_factory) as session:
            OrderRepository.create_order(
                session,
                NewOrderDomain(
                    id=order_id,
                    account_id=test_account_id,
                    amount=order_amount,
                    status=OrderStatus.CREATED,
                ),
            )

        event = generate_request_event(
            body={
                "sender": "0x1234",
                "recipient": "0x5678",
                "orderId": order_id,
                "transactionHash": "0xabcde",
            }
        )

        response = save_evm_transaction(event, None, test_billing_service, test_auth_service)
        validate_response_ok(response)

        with session_scope(test_session_factory) as session:
            order = OrderRepository.get_order(session, order_id)

        assert order.status == OrderStatus.PROCESSING
        assert len(order.evm_transactions) == 1
        assert order.evm_transactions[0].status == EVMTransactionStatus.PENDING
        assert order.evm_transactions[0].order_id == order_id

    def test_get_balance_ok(self, test_billing_service, add_test_account_balance):
        test_balance = add_test_account_balance

        response = get_balance(None, None, test_billing_service)
        _, data = validate_response_ok(response)

        assert data.get("balanceInCogs") == test_balance

    def test_get_balance_history_ok(self):
        pass