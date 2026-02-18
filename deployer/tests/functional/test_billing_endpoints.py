from decimal import Decimal

import deepdiff
import pytest

from common.logger import get_logger
from deployer.application.handlers.billing_handlers import (
    create_order,
    save_evm_transaction,
    get_balance,
    get_balance_history,
    get_metrics,
    get_balance_and_rate,
    update_transaction_status,
    call_event_consumer,
    update_token_rate,
)
from deployer.application.services.billing_service import BillingService
from deployer.application.services.metrics_service import MetricsService
from deployer.config import TOKEN_DECIMALS, TOKEN_NAME
from deployer.exceptions import HostedServiceNotFoundException
from deployer.infrastructure.db import session_scope
from deployer.infrastructure.models import OrderStatus, EVMTransactionStatus
from deployer.infrastructure.repositories.account_balance_repository import AccountBalanceRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.infrastructure.repositories.token_rate_repository import TokenRateRepository
from deployer.tests.functional.utils import (
    validate_response_ok,
    generate_request_event,
    create_order_and_transaction,
    add_transactions_metadata,
    create_common_queue_event,
    validate_response_bad_request,
    add_order,
    validate_response_forbidden,
    validate_response_not_found,
)

logger = get_logger(__name__)


class TestCreateOrder:
    def test_create_order_ok(self, test_billing_service, test_session_factory):
        order_amount = 123
        event = generate_request_event(body={"amount": order_amount})

        response = create_order(event, None, test_billing_service)
        _, data = validate_response_ok(response)

        response_order_id = data.get("orderId")
        assert response_order_id is not None and response_order_id != "", (
            f"No ORDER ID in the response! Response data: {data}"
        )

        with session_scope(test_session_factory) as session:
            order = OrderRepository.get_order(session, response_order_id)

        assert order is not None, "Order has not been created!"
        assert order.amount == order_amount

    def test_create_existing_order_ok(
        self, test_billing_service, test_session_factory, add_test_account_balance
    ):
        order_amount = 123
        order_id = "123"

        with session_scope(test_session_factory) as session:
            add_order(
                session, order_id=order_id, amount=order_amount, order_status=OrderStatus.CREATED
            )

        event = generate_request_event(body={"amount": order_amount})

        response = create_order(event, None, test_billing_service)
        _, data = validate_response_ok(response)

        response_order_id = data.get("orderId")
        assert response_order_id == order_id

        with session_scope(test_session_factory) as session:
            order = OrderRepository.get_order(session, response_order_id)

        assert order is not None, "Order has not been created!"
        assert order.amount == order_amount

    def test_create_order_old_cancelled_ok(
        self, test_billing_service, test_session_factory, add_test_account_balance
    ):
        first_order_id = "123"

        with session_scope(test_session_factory) as session:
            add_order(session, order_id=first_order_id, amount=12, order_status=OrderStatus.CREATED)

        order_amount = 123
        event = generate_request_event(body={"amount": order_amount})

        response = create_order(event, None, test_billing_service)
        _, data = validate_response_ok(response)

        response_order_id = data.get("orderId")
        assert response_order_id is not None and response_order_id != "", (
            f"No ORDER ID in the response! Response data: {data}"
        )

        with session_scope(test_session_factory) as session:
            first_order = OrderRepository.get_order(session, first_order_id)
            order = OrderRepository.get_order(session, response_order_id)

        assert first_order.status == OrderStatus.CANCELLED
        assert order is not None, "Order has not been created!"
        assert order.amount == order_amount

    def test_create_order_zero_amount(self):
        order_amount = 0
        event = generate_request_event(body={"amount": order_amount})

        response = create_order(event, None)
        _, message = validate_response_bad_request(response)

        assert message == "Validation failed for request body."

    def test_create_order_missing_body(self):
        response = create_order({}, None)
        _, message = validate_response_bad_request(response)

        assert message == "Missing body"


class TestSaveEVMTransaction:
    def test_save_evm_transaction_ok(
        self,
        test_billing_service,
        test_auth_service,
        test_session_factory,
        add_test_account_balance,
        test_account_id,
    ):
        with session_scope(test_session_factory) as session:
            new_order = add_order(session, "123", amount=123, order_status=OrderStatus.CREATED)

        event = generate_request_event(
            body={
                "sender": "0x1234",
                "recipient": "0x5678",
                "orderId": new_order.id,
                "transactionHash": "0xabcde",
            }
        )

        response = save_evm_transaction(event, None, test_billing_service, test_auth_service)
        validate_response_ok(response)

        with session_scope(test_session_factory) as session:
            order = OrderRepository.get_order(session, new_order.id)

        assert order.status == OrderStatus.PROCESSING
        assert len(order.evm_transactions) == 1
        assert order.evm_transactions[0].status == EVMTransactionStatus.PENDING
        assert order.evm_transactions[0].order_id == new_order.id

    def test_save_evm_transaction_incorrect_order_status(
        self,
        test_billing_service,
        test_auth_service,
        test_session_factory,
        add_test_account_balance,
    ):
        order_id = "123"
        order_status = OrderStatus.CANCELLED

        with session_scope(test_session_factory) as session:
            add_order(session, "123", amount=123, order_status=order_status)

        event = generate_request_event(
            body={
                "sender": "0x1234",
                "recipient": "0x5678",
                "orderId": order_id,
                "transactionHash": "0xabcde",
            }
        )

        response = save_evm_transaction(event, None, test_billing_service, test_auth_service)
        _, message = validate_response_bad_request(response)

        assert message == f"Order status {order_status.value} is not acceptable for this operation!"

    def test_save_evm_transaction_missing_fields(self):
        event = generate_request_event(body={"transactionHash": "0xabcde"})

        response = save_evm_transaction(event, None)
        _, message = validate_response_bad_request(response)

        assert message == "Validation failed for request body."

    def test_save_evm_transaction_missing_body(self):
        response = save_evm_transaction({}, None)
        _, message = validate_response_bad_request(response)

        assert message == "Missing body"

    def test_save_evm_transaction_no_order(self, test_auth_service):
        event = generate_request_event(
            body={
                "sender": "0x1234",
                "recipient": "0x5678",
                "orderId": "test_order_id",
                "transactionHash": "0xabcde",
            }
        )

        response = save_evm_transaction(event, None, auth_service=test_auth_service)
        _, message = validate_response_forbidden(response)

        assert message == "Access denied"


class TestGetBalance:
    def test_get_balance_ok(self, test_billing_service, add_test_account_balance):
        test_balance = add_test_account_balance

        response = get_balance(None, None, test_billing_service)
        _, data = validate_response_ok(response)

        assert data.get("balanceInCogs") == test_balance

    def test_get_balance_no_account_balance_ok(self, test_billing_service):

        response = get_balance(None, None, test_billing_service)
        _, data = validate_response_ok(response)

        assert data.get("balanceInCogs") == 0


class TestGetBalanceHistory:
    def test_get_balance_history_ok(
        self, test_haas_client_with_events, test_session_factory, add_test_orders
    ):
        billing_service = BillingService(
            session_factory=test_session_factory, haas_client=test_haas_client_with_events
        )

        event = generate_request_event(
            query_parameters={"limit": 5, "page": 1, "order": "desc", "period": "day"}
        )

        response = get_balance_history(event, None, billing_service)
        _, data = validate_response_ok(response)

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

    def test_get_balance_history_empty_ok(self, test_billing_service, test_session_factory):
        event = generate_request_event(
            query_parameters={"limit": 5, "page": 1, "order": "desc", "period": "day"}
        )

        response = get_balance_history(event, None, test_billing_service)
        _, data = validate_response_ok(response)

        assert data["events"] == []
        assert data["totalCount"] == 0

    def test_get_balance_history_incorrect_filters(self):
        event = generate_request_event(
            query_parameters={
                "limit": 5,
                "page": 1,
                "order": "desc",
                "period": "day",
                "type": "expense",
                "status": "success",
            }
        )

        response = get_balance_history(event, None)
        _, message = validate_response_bad_request(response)

        assert message == "There must be only 'all' status parameter for 'expense' type!"


class TestGetMetrics:
    def test_get_metrics_ok(
        self,
        test_auth_service,
        test_haas_client_with_events,
        test_session_factory,
        add_test_daemon_and_service,
        test_hosted_service_id,
    ):
        metrics_service = MetricsService(
            session_factory=test_session_factory, haas_client=test_haas_client_with_events
        )

        event = generate_request_event(
            path_parameters={"hostedServiceId": test_hosted_service_id},
            query_parameters={"period": "day"},
        )

        response = get_metrics(event, None, metrics_service, test_auth_service)
        _, data = validate_response_ok(response)

        assert len(data["labels"]) in [20, 21]
        assert data["summary"]["requests"]["total"] in [20, 21]
        assert all(len(value) in [20, 21] for value in data["values"].values())

    def test_get_metrics_empty_ok(
        self,
        test_metrics_service,
        test_auth_service,
        test_session_factory,
        add_test_daemon_and_service,
        test_hosted_service_id,
    ):
        event = generate_request_event(
            path_parameters={"hostedServiceId": test_hosted_service_id},
            query_parameters={"period": "day"},
        )

        response = get_metrics(event, None, test_metrics_service, test_auth_service)
        _, data = validate_response_ok(response)

        expected_response = test_metrics_service._get_empty_metrics_response()
        diff = deepdiff.DeepDiff(expected_response, data)

        assert diff == {}

    def test_get_metrics_no_service(
        self,
        test_metrics_service,
        test_auth_service,
        test_hosted_service_id,
    ):
        event = generate_request_event(
            path_parameters={"hostedServiceId": test_hosted_service_id},
            query_parameters={"period": "day"},
        )

        response = get_metrics(event, None, test_metrics_service, test_auth_service)
        _, message = validate_response_forbidden(response)

        assert message == "Access denied"


class TestGetBalanceAndRate:
    def test_get_balance_and_rate_ok(
        self,
        test_billing_service,
        add_token_rate_records,
        add_test_account_balance,
        add_test_daemon_and_service,
        test_org_id,
        test_service_id,
    ):
        token_rate = round(add_token_rate_records)
        balance = add_test_account_balance

        event = generate_request_event(
            query_parameters={"orgId": test_org_id, "serviceId": test_service_id}
        )

        response = get_balance_and_rate(event, None, test_billing_service)
        _, data = validate_response_ok(response)

        assert data["balanceInCogs"] == balance
        assert data["cogsPerUsd"] == token_rate

    def test_get_balance_and_rate_no_account_balance_ok(
        self,
        test_billing_service,
        add_token_rate_records,
        test_org_id,
        test_service_id,
    ):
        token_rate = round(add_token_rate_records)

        event = generate_request_event(
            query_parameters={"orgId": test_org_id, "serviceId": test_service_id}
        )

        response = get_balance_and_rate(event, None, test_billing_service)
        _, data = validate_response_ok(response)

        assert data["balanceInCogs"] == 0
        assert data["cogsPerUsd"] == token_rate

    def test_get_balance_and_rate_no_token_rate(
        self,
        test_billing_service,
        test_org_id,
        test_service_id,
    ):
        event = generate_request_event(
            query_parameters={"orgId": test_org_id, "serviceId": test_service_id}
        )

        response = get_balance_and_rate(event, None, test_billing_service)
        _, message = validate_response_not_found(response)

        assert message == "There is no data about token rate for now!"


class TestUpdateTransactionStatus:
    def test_update_transaction_status_ok(
        self,
        test_billing_service,
        test_session_factory,
        add_test_account_balance,
        test_account_id,
        monkeypatch,
    ):
        with session_scope(test_session_factory) as session:
            new_order, transaction = create_order_and_transaction(
                session, account_id=test_account_id
            )
            add_transactions_metadata(session)

        def mock_get_transactions_from_blockchain(*args, **kwargs):
            transaction.status = EVMTransactionStatus.SUCCESS
            return [(transaction, new_order.amount)], 950

        monkeypatch.setattr(
            BillingService,
            "_get_transactions_from_blockchain",
            mock_get_transactions_from_blockchain,
        )

        update_transaction_status(None, None, test_billing_service)

        with session_scope(test_session_factory) as session:
            order = OrderRepository.get_order(session, order_id=new_order.id)
            account_balance = AccountBalanceRepository.get_account_balance(session, test_account_id)

        assert order.status == OrderStatus.SUCCESS
        assert account_balance.balance_in_cogs == add_test_account_balance + order.amount
        assert order.evm_transactions[0].status == EVMTransactionStatus.SUCCESS


class TestCallEventConsumer:
    def test_call_event_consumer_ok(
        self,
        test_billing_service,
        test_session_factory,
        add_test_account_balance,
        add_test_daemon_and_service,
        test_org_id,
        test_service_id,
        test_account_id,
    ):
        amount = 10
        balance = add_test_account_balance

        event = generate_request_event(
            orgId=test_org_id,
            serviceId=test_service_id,
            duration=10,
            amount=amount,
            timestamp="2025-10-16T18:08:42.782000",
        )
        queue_event = create_common_queue_event([event])
        call_event_consumer(queue_event, None, test_billing_service)

        with session_scope(test_session_factory) as session:
            account_balance = AccountBalanceRepository.get_account_balance(session, test_account_id)

        assert account_balance.balance_in_cogs == balance - amount

    def test_call_event_consumer_no_service(
        self,
        test_billing_service,
        test_session_factory,
        test_org_id,
        test_service_id,
        test_account_id,
    ):
        amount = 10

        event = generate_request_event(
            orgId=test_org_id,
            serviceId=test_service_id,
            duration=10,
            amount=amount,
            timestamp="2025-10-16T18:08:42.782000",
        )
        queue_event = create_common_queue_event([event])

        with pytest.raises(HostedServiceNotFoundException) as e:
            call_event_consumer(queue_event, None, test_billing_service)

        assert e.type == HostedServiceNotFoundException
        assert f"Hosted service for service with org_id={test_org_id} and service_id={test_service_id} not found!" in str(e.value)


class TestUpdateTokenRate:
    def test_update_token_rate(
        self, test_billing_service, test_session_factory, add_token_rate_records
    ):
        test_token_rate = 0.5
        test_cogs_per_usd = round(10**TOKEN_DECIMALS / test_token_rate)

        test_billing_service._crypto_exchange_client.token_rate = test_token_rate
        update_token_rate(None, None, billing_service=test_billing_service)

        with session_scope(test_session_factory) as session:
            token_rate = TokenRateRepository.get_average_cogs_per_usd(session, TOKEN_NAME)

        new_cogs_per_usd = round(
            Decimal(add_token_rate_records * 10 + test_cogs_per_usd) / Decimal(11)
        )
        assert token_rate == new_cogs_per_usd
