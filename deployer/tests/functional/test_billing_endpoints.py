from deployer.application.handlers.billing_handlers import create_order, save_evm_transaction, get_balance, \
    get_balance_history, get_metrics
from deployer.application.services.billing_service import BillingService
from deployer.application.services.metrics_service import MetricsService
from deployer.domain.models.order import NewOrderDomain
from deployer.infrastructure.db import session_scope
from deployer.infrastructure.models import OrderStatus, EVMTransactionStatus
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.tests.functional.utils import validate_response_ok, generate_request_event


class TestBillingEndpoints:
    def test_create_order_ok(self, test_billing_service, test_session_factory):
        order_amount = 123
        event = generate_request_event(body={"amount": order_amount})

        response = create_order(event, None, test_billing_service)

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

    def test_get_balance_history_ok(self, test_haas_client_with_events, test_session_factory, add_test_orders):
        billing_service = BillingService(session_factory = test_session_factory, haas_client = test_haas_client_with_events)

        event = generate_request_event(
            query_parameters = {
                "limit": 5,
                "page": 1,
                "order": "desc",
                "period": "day"
            }
        )

        response = get_balance_history(event, None, billing_service)
        status, data = validate_response_ok(response)

        assert len(data["events"]) == 5
        assert data["totalCount"] == 23

        income_count = 0
        income_sum = 0
        expense_count = 0
        expense_sum = 0
        for i in range(5):
            if data["events"][i]["type"] == "income":
                income_count += 1
                income_sum += data["events"][i]["amount"]
            elif data["events"][i]["type"] == "expense":
                expense_count += 1
                expense_sum += data["events"][i]["amount"]

        assert income_count == 3
        assert income_sum == 3003
        assert expense_count == 2
        assert expense_sum == 201

    def test_get_metrics(self, test_auth_service, test_haas_client_with_events, test_session_factory, add_test_daemon_and_service, test_hosted_service_id):
        metrics_service = MetricsService(session_factory = test_session_factory, haas_client = test_haas_client_with_events)

        event = generate_request_event(
            path_parameters = {"hostedServiceId": test_hosted_service_id},
            query_parameters = {"period": "day"}
        )

        response = get_metrics(event, None, metrics_service, test_auth_service)
        status, data = validate_response_ok(response)
        print(data)

        assert len(data["labels"]) == 20
        for value in data["values"].values():
            assert len(value) == 20
        assert data["summary"]["requests"]["total"] == 20

    def test_get_balance_and_rate_ok(self):
        pass

    def test_update_transaction_status(self):
        pass

    def test_call_event_consumer(self):
        pass

    def update_token_rate(self):
        pass
