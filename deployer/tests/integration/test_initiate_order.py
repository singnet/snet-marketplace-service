"""
Integration tests for initiate_order handler.
"""

import json

from deployer.application.handlers.order_handlers import initiate_order
from deployer.infrastructure.models import DaemonStatus, OrderStatus
from common.constant import StatusCode


class TestInitiateOrderHandler:
    """Test cases for initiate_order handler."""

    def test_initiate_order_success_new_daemon(
        self, initiate_order_event, lambda_context, db_session, daemon_repo, order_repo
    ):
        """Test successful order initiation with new daemon creation."""
        # Arrange
        event = initiate_order_event
        event["body"] = json.dumps(
            {
                "orgId": "test-org-new",
                "serviceId": "test-service-new",
                "serviceEndpoint": "https://test-endpoint.com",
            }
        )

        # Act
        response = initiate_order(event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK

        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert "orderId" in body["data"]
        assert body["data"]["orderId"] is not None

        # Verify daemon was created
        daemon = daemon_repo.search_daemon(db_session, "test-org-new", "test-service-new")
        assert daemon is not None
        assert daemon.org_id == "test-org-new"
        assert daemon.service_id == "test-service-new"
        assert daemon.status == DaemonStatus.INIT
        assert daemon.daemon_config["service_endpoint"] == "https://test-endpoint.com"

        # Verify order was created
        order = order_repo.get_order(db_session, body["data"]["orderId"])
        assert order is not None
        assert order.daemon_id == daemon.id
        assert order.status == OrderStatus.PROCESSING

    def test_initiate_order_success_existing_daemon_topup(
        self, initiate_order_event, lambda_context, db_session, test_daemon_up, order_repo
    ):
        """Test successful order initiation for existing daemon (top-up scenario)."""
        # Arrange
        event = initiate_order_event
        event["body"] = json.dumps(
            {"orgId": test_daemon_up.org_id, "serviceId": test_daemon_up.service_id}
        )

        # Act
        response = initiate_order(event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK

        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert "orderId" in body["data"]

        # Verify order was created for existing daemon
        order = order_repo.get_order(db_session, body["data"]["orderId"])
        assert order is not None
        assert order.daemon_id == test_daemon_up.id
        assert order.status == OrderStatus.PROCESSING

    def test_initiate_order_authorization_check(self, initiate_order_event, lambda_context):
        """Test that authorization is actually being checked (not mocked)."""
        # Arrange - remove authorization from event
        event = initiate_order_event
        event["requestContext"] = {}  # No authorization

        # Act
        response = initiate_order(event, lambda_context)

        # Assert - should fail with 400 (RequestContext throws BadRequestException)
        assert response["statusCode"] == StatusCode.BAD_REQUEST
