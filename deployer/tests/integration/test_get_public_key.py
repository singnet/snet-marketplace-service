"""
Integration tests for get_public_key handler.
"""
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
        
        # Verify HaaS client was called once
        mock_haas_client.get_public_key.assert_called_once()

    def test_get_public_key_empty_response(
        self,
        authorized_event,
        lambda_context,
        mock_haas_client,
    ):
        """Test handling of empty public key from HaaS."""
        # Arrange
        mock_haas_client.get_public_key.return_value = ""

        # Act
        response = get_public_key(authorized_event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        data = body["data"]
        assert "publicKey" in data
        assert data["publicKey"] == ""  # Empty key is still returned
        
    def test_get_public_key_different_key_formats(
        self,
        authorized_event,
        lambda_context,
        mock_haas_client,
    ):
        """Test handling of different SSH key formats."""
        # Test different valid SSH key formats
        test_keys = [
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl",
            "ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBtest",
            "ssh-dss AAAAB3NzaC1kc3MAAACBAP1/U4EddRIpUt9KnC7s5Of2EbdSPO9EAMMetest"
        ]
        
        for test_key in test_keys:
            # Arrange
            mock_haas_client.reset_mock()
            mock_haas_client.get_public_key.return_value = test_key

            # Act
            response = get_public_key(authorized_event, lambda_context)

            # Assert
            assert response["statusCode"] == StatusCode.OK
            body = json.loads(response["body"])
            assert body["status"] == "success"
            
            data = body["data"]
            assert data["publicKey"] == test_key
            
            mock_haas_client.get_public_key.assert_called_once()
