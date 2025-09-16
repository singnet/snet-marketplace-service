import json

from deployer.application.handlers.daemon_handlers import get_public_key
from common.constant import StatusCode


class TestGetPublicKeyHandler:
    """Test cases for get_public_key handler."""

    def test_get_public_key_success(
        self,
        authorized_event,
        lambda_context,
        mock_haas_client,
    ):
        """Test successful public key retrieval from HaaS."""
        # Arrange
        # HaaS client is mocked via conftest; set expected return value here.
        mock_haas_client.get_public_key.return_value = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCtest"

        # Act
        response = get_public_key(authorized_event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert "data" in body and "error" in body

        data = body["data"]
        assert "publicKey" in data
        assert data["publicKey"] == "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCtest"