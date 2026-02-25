import datetime
from datetime import timedelta
from decimal import Decimal
from random import random
from typing import List

import pytest

from deployer.application.services.authorization_service import AuthorizationService
from deployer.application.services.billing_service import BillingService
from deployer.application.services.daemon_service import DaemonService
from deployer.application.services.deployments_service import DeploymentsService
from deployer.application.services.hosted_services_service import HostedServicesService
from deployer.application.services.metrics_service import MetricsService
from deployer.config import TOKEN_NAME, TOKEN_DECIMALS
from deployer.domain.models.account_balance import NewAccountBalanceDomain
from deployer.domain.models.hosted_service import NewHostedServiceDomain
from deployer.domain.models.token_rate import NewTokenRateDomain
from deployer.domain.schemas.haas_responses import CallEventResponse, GetCallEventsResponse
from deployer.infrastructure.db import session_scope
from deployer.infrastructure.models import (
    OrderStatus,
    EVMTransactionStatus,
    HostedServiceStatus,
)
from deployer.infrastructure.repositories.account_balance_repository import AccountBalanceRepository
from deployer.infrastructure.repositories.hosted_service_repository import HostedServiceRepository
from deployer.infrastructure.repositories.token_rate_repository import TokenRateRepository
from deployer.tests.functional.utils import create_order_and_transaction, add_daemon


@pytest.fixture(scope="function")
def test_auth_service(test_session_factory, test_registry_client):
    return AuthorizationService(test_session_factory, test_registry_client)


@pytest.fixture(scope="function")
def test_billing_service(test_session_factory, test_haas_client, test_crypto_exchange_client):
    return BillingService(test_session_factory, test_haas_client, test_crypto_exchange_client)


@pytest.fixture(scope="function")
def test_daemon_service(test_session_factory, test_deployer_client, test_haas_client):
    return DaemonService(test_session_factory, test_deployer_client, test_haas_client)


@pytest.fixture(scope="function")
def test_deployments_service(test_session_factory, test_deployer_client, test_haas_client):
    return DeploymentsService(test_session_factory, test_deployer_client, test_haas_client)


@pytest.fixture(scope="function")
def test_hosted_services_service(test_session_factory, test_haas_client, test_github_api_client):
    return HostedServicesService(test_session_factory, test_haas_client, test_github_api_client)


@pytest.fixture(scope="function")
def test_metrics_service(test_session_factory, test_haas_client):
    return MetricsService(test_session_factory, test_haas_client)


@pytest.fixture(scope="function")
def add_test_account_balance(test_session_factory, test_account_id):
    balance = 123
    with session_scope(test_session_factory) as session:
        AccountBalanceRepository.upsert_account_balance(
            session, NewAccountBalanceDomain(account_id=test_account_id, balance_in_cogs=balance)
        )
    return balance


@pytest.fixture(scope="function")
def test_haas_client_with_events(test_haas_client, test_org_id, test_service_id):
    events = []
    total_count = 20
    current_time = datetime.datetime.now(datetime.UTC)

    for i in range(total_count):
        duration = 10 + i
        amount = 100 + i
        timestamp = current_time - timedelta(minutes=i, hours=i)
        event = CallEventResponse(
            orgId=test_org_id,
            serviceId=test_service_id,
            duration=duration,
            amount=amount,
            timestamp=timestamp,
        )
        events.append(event)

    test_haas_client.call_events = GetCallEventsResponse(events=events, totalCount=total_count)

    return test_haas_client


@pytest.fixture(scope="function")
def add_test_orders(test_session_factory, add_test_account_balance, test_account_id):
    total_count = 3
    with session_scope(test_session_factory) as session:
        for i in range(total_count):
            create_order_and_transaction(
                session,
                order_id=f"order_{i}",
                account_id=test_account_id,
                amount=1000 + i,
                order_status=OrderStatus.SUCCESS,
                tx_hash=f"0xhash{i}",
                tx_status=EVMTransactionStatus.SUCCESS,
                sender=f"0xsender{i}",
            )


@pytest.fixture(scope="function")
def add_test_daemon_and_service(
    test_session_factory,
    add_test_account_balance,
    test_account_id,
    test_org_id,
    test_service_id,
    test_daemon_id,
    test_hosted_service_id,
):
    with session_scope(test_session_factory) as session:
        add_daemon(session, test_account_id, test_org_id, test_service_id, test_daemon_id)
        HostedServiceRepository.create_hosted_service(
            session,
            NewHostedServiceDomain(
                id=test_hosted_service_id,
                daemon_id=test_daemon_id,
                status=HostedServiceStatus.UP,
                github_account_name="",
                github_repository_name="",
                last_commit_url="",
            ),
        )


@pytest.fixture(scope="function")
def add_token_rate_records(test_session_factory):
    total_count = 10
    cogs_sum = 0
    with session_scope(test_session_factory) as session:
        for _ in range(total_count):
            usd_per_token = round((random() * 0.9) + 0.1, 2)  # [0.1, 1)
            cogs_per_usd = round(10**TOKEN_DECIMALS / usd_per_token)
            cogs_sum += cogs_per_usd
            TokenRateRepository.add_token_rate(
                session,
                NewTokenRateDomain(
                    token_symbol=TOKEN_NAME, usd_per_token=usd_per_token, cogs_per_usd=cogs_per_usd
                ),
            )
    return Decimal(cogs_sum) / Decimal(total_count)


@pytest.fixture(scope="function")
def add_test_daemon(
    test_session_factory,
    add_test_account_balance,
    test_account_id,
    test_org_id,
    test_service_id,
    test_daemon_id,
):
    with session_scope(test_session_factory) as session:
        add_daemon(session, test_account_id, test_org_id, test_service_id, test_daemon_id)


@pytest.fixture(scope = "function")
def test_service_endpoint() -> str:
    return "http://localhost:8080"


@pytest.fixture(scope = "function")
def test_service_credentials() -> List[dict]:
    return [{"key": "Authorization", "value": "Bearer 1234567890", "location": "headers"}]
