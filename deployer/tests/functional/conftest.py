import pytest

from deployer.application.services.authorization_service import AuthorizationService
from deployer.application.services.billing_service import BillingService
from deployer.application.services.daemon_service import DaemonService
from deployer.application.services.deployments_service import DeploymentsService
from deployer.application.services.hosted_services_service import HostedServicesService
from deployer.application.services.metrics_service import MetricsService
from deployer.domain.models.account_balance import NewAccountBalanceDomain
from deployer.infrastructure.db import session_scope
from deployer.infrastructure.repositories.account_balance_repository import AccountBalanceRepository


@pytest.fixture(scope="function")
def test_auth_service(test_session_factory, test_registry_client):
    return AuthorizationService(test_session_factory, test_registry_client)


@pytest.fixture(scope="function")
def test_billing_service(test_session_factory, test_haas_client):
    return BillingService(test_session_factory, test_haas_client)


@pytest.fixture(scope="function")
def test_daemon_service(test_session_factory, test_deployer_client, test_haas_client):
    return DaemonService(test_session_factory, test_deployer_client, test_haas_client)


@pytest.fixture(scope="function")
def test_deployments_service(test_session_factory, test_deployer_client, test_haas_client):
    return DeploymentsService(test_session_factory, test_deployer_client, test_haas_client)


@pytest.fixture(scope="function")
def test_hosted_services_service(test_session_factory, test_haas_client):
    return HostedServicesService(test_session_factory, test_haas_client)


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
