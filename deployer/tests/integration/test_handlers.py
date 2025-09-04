import pytest
import json
from datetime import datetime, UTC, timedelta
from unittest.mock import Mock, patch, MagicMock
from http import HTTPStatus

from deployer.infrastructure.models import DaemonStatus, OrderStatus, EVMTransactionStatus, ClaimingPeriodStatus
from deployer.application.handlers import daemon_handlers, order_handlers, transaction_handlers, job_handlers
from deployer.exceptions import DaemonNotFoundException


class TestOrderHandlers:
    """Tests for order-related handlers."""
    
    def test_initiate_order_new_daemon(self, db_session, create_lambda_event, order_repo, daemon_repo):
        """Test initiating order for new daemon."""
        event = create_lambda_event(
            method="POST",
            body={
                "orgId": "new-org",
                "serviceId": "new-service",
                "serviceEndpoint": "https://new-endpoint.com",
                "serviceCredentials": [{"key": "API_KEY", "value": "secret", "location": "header"}]
            }
        )
        
        response = order_handlers.initiate_order(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert "orderId" in body["data"]
        
        # Verify daemon created
        daemon = daemon_repo.search_daemon(db_session, "new-org", "new-service")
        assert daemon is not None
        assert daemon.status == DaemonStatus.INIT
        assert daemon.daemon_config["service_endpoint"] == "https://new-endpoint.com"
        
        # Verify order created
        order = order_repo.get_order(db_session, body["data"]["orderId"])
        assert order is not None
        assert order.status == OrderStatus.PROCESSING
    
    def test_initiate_order_existing_daemon(self, db_session, create_lambda_event, base_daemon, daemon_repo):
        """Test initiating order for existing daemon (top-up)."""
        # Update daemon to UP status
        daemon_repo.update_daemon_status(db_session, base_daemon.id, DaemonStatus.UP)
        db_session.commit()
        
        event = create_lambda_event(
            method="POST",
            body={
                "orgId": base_daemon.org_id,
                "serviceId": base_daemon.service_id
            }
        )
        
        response = order_handlers.initiate_order(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert "orderId" in body["data"]
    
    def test_get_order(self, db_session, create_lambda_event, base_order):
        """Test getting order details."""
        event = create_lambda_event(
            path_params={"orderId": base_order.id}
        )
        
        response = order_handlers.get_order(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["data"]["id"] == base_order.id
        assert body["data"]["status"] == OrderStatus.PROCESSING.value


class TestTransactionHandlers:
    """Tests for transaction-related handlers."""
    
    def test_save_evm_transaction(self, db_session, create_lambda_event, base_order, transaction_repo):
        """Test saving EVM transaction."""
        event = create_lambda_event(
            method="POST",
            body={
                "orderId": base_order.id,
                "transactionHash": "0xNewTransactionHash",
                "sender": "0xSenderAddress",
                "recipient": "0xRecipientAddress"
            }
        )
        
        response = transaction_handlers.save_evm_transaction(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        # Verify transaction saved
        transaction = transaction_repo.get_transaction(db_session, "0xNewTransactionHash")
        assert transaction is not None
        assert transaction.order_id == base_order.id
        assert transaction.status == EVMTransactionStatus.PENDING


class TestDaemonHandlers:
    """Tests for daemon-related handlers."""
    
    def test_get_user_daemons(self, db_session, create_lambda_event, base_daemon, base_claiming_period):
        """Test getting user's daemons."""
        event = create_lambda_event()
        
        response = daemon_handlers.get_user_daemons(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert len(body["data"]) == 1
        
        daemon_data = body["data"][0]
        assert daemon_data["id"] == base_daemon.id
        assert daemon_data["status"] == DaemonStatus.INIT.value
        assert "lastClaimedAt" in daemon_data
    
    def test_get_service_daemon(self, db_session, create_lambda_event, base_daemon, base_order):
        """Test getting specific daemon details."""
        event = create_lambda_event(
            path_params={"daemonId": base_daemon.id}
        )
        
        response = daemon_handlers.get_service_daemon(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        data = body["data"]
        assert data["id"] == base_daemon.id
        assert data["orgId"] == base_daemon.org_id
        assert data["serviceId"] == base_daemon.service_id
        assert "orders" in data
        assert len(data["orders"]) == 1
    
    def test_start_daemon_for_claiming(self, db_session, create_lambda_event, base_daemon, 
                                       daemon_repo, mock_deployer_client):
        """Test starting daemon for claiming period."""
        # Update daemon to DOWN status
        daemon_repo.update_daemon_status(db_session, base_daemon.id, DaemonStatus.DOWN)
        db_session.commit()
        
        event = create_lambda_event(
            path_params={"daemonId": base_daemon.id}
        )
        
        response = daemon_handlers.start_daemon_for_claiming(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        # Verify claiming period created
        from deployer.infrastructure.repositories.claiming_period_repository import ClaimingPeriodRepository
        claiming_period = ClaimingPeriodRepository.get_last_claiming_period(db_session, base_daemon.id)
        assert claiming_period is not None
        assert claiming_period.status == ClaimingPeriodStatus.ACTIVE
        
        # Verify deployer client called
        mock_deployer_client.start_daemon.assert_called_once_with(base_daemon.id)
    
    def test_get_public_key(self, create_lambda_event, mock_haas_client):
        """Test getting public key from HaaS."""
        event = create_lambda_event()
        
        response = daemon_handlers.get_public_key(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["data"]["publicKey"] == "test-public-key-123"
    
    def test_update_config(self, db_session, create_lambda_event, base_daemon, daemon_repo):
        """Test updating daemon configuration."""
        event = create_lambda_event(
            method="POST",
            path_params={"daemonId": base_daemon.id},
            body={
                "serviceEndpoint": "https://updated-endpoint.com",
                "serviceCredentials": [{"key": "NEW_KEY", "value": "new_secret", "location": "header"}]
            }
        )
        
        response = daemon_handlers.update_config(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        # Verify config updated
        daemon = daemon_repo.get_daemon(db_session, base_daemon.id)
        assert daemon.daemon_config["service_endpoint"] == "https://updated-endpoint.com"
        assert daemon.daemon_config["service_credentials"][0]["key"] == "NEW_KEY"
    
    def test_search_daemon(self, db_session, create_lambda_event, base_daemon, base_order):
        """Test searching for daemon by org and service."""
        event = create_lambda_event(
            query_params={
                "orgId": base_daemon.org_id,
                "serviceId": base_daemon.service_id
            }
        )
        
        response = daemon_handlers.search_daemon(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        data = body["data"]
        assert "daemon" in data
        assert data["daemon"]["id"] == base_daemon.id
        assert "order" in data
        assert data["order"]["id"] == base_order.id
    
    def test_start_daemon(self, db_session, create_lambda_event, base_daemon, 
                         daemon_repo, mock_haas_client):
        """Test starting daemon."""
        # Update daemon to READY_TO_START status
        daemon_repo.update_daemon_status(db_session, base_daemon.id, DaemonStatus.READY_TO_START)
        db_session.commit()
        
        event = create_lambda_event(
            path_params={"daemonId": base_daemon.id}
        )
        
        response = daemon_handlers.start_daemon(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        # Verify HaaS client called
        mock_haas_client.start_daemon.assert_called_once()
        
        # Verify daemon status updated
        daemon = daemon_repo.get_daemon(db_session, base_daemon.id)
        assert daemon.status == DaemonStatus.STARTING
    
    def test_stop_daemon(self, db_session, create_lambda_event, base_daemon, 
                        daemon_repo, mock_haas_client):
        """Test stopping daemon."""
        # Update daemon to UP status
        daemon_repo.update_daemon_status(db_session, base_daemon.id, DaemonStatus.UP)
        db_session.commit()
        
        event = create_lambda_event(
            path_params={"daemonId": base_daemon.id}
        )
        
        response = daemon_handlers.stop_daemon(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        # Verify HaaS client called
        mock_haas_client.delete_daemon.assert_called_once()
        
        # Verify daemon status updated
        daemon = daemon_repo.get_daemon(db_session, base_daemon.id)
        assert daemon.status == DaemonStatus.DELETING
    
    def test_redeploy_daemon(self, db_session, create_lambda_event, base_daemon, 
                            daemon_repo, mock_haas_client):
        """Test redeploying daemon."""
        # Update daemon to UP status
        daemon_repo.update_daemon_status(db_session, base_daemon.id, DaemonStatus.UP)
        db_session.commit()
        
        event = create_lambda_event(
            path_params={"daemonId": base_daemon.id}
        )
        
        response = daemon_handlers.redeploy_daemon(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        # Verify HaaS client called
        mock_haas_client.redeploy_daemon.assert_called_once()
        
        # Verify daemon status updated
        daemon = daemon_repo.get_daemon(db_session, base_daemon.id)
        assert daemon.status == DaemonStatus.RESTARTING


class TestJobHandlers:
    """Tests for job-related handlers."""
    
    def test_registry_event_consumer_service_created(self, db_session, base_daemon, 
                                                     daemon_repo, mock_storage_provider):
        """Test processing ServiceCreated event."""
        event = {
            "Records": [{
                "body": json.dumps({
                    "Message": json.dumps({
                        "blockchain_event": {
                            "name": "ServiceCreated",
                            "data": {
                                "json_str": str({
                                    "orgId": base_daemon.org_id.encode(),
                                    "serviceId": base_daemon.service_id.encode(),
                                    "metadataURI": b"ipfs://metadata-uri"
                                })
                            }
                        }
                    })
                })
            }]
        }
        
        # Mock tar file processing
        with patch('deployer.application.services.job_services.JobService._get_service_class') as mock_class:
            mock_class.return_value = "test.ServiceClass"
            
            response = job_handlers.registry_event_consumer(event, context=None)
        
        assert response == {}
        
        # Verify daemon updated
        daemon = daemon_repo.get_daemon(db_session, base_daemon.id)
        assert daemon.service_published is True
        assert daemon.daemon_config["daemon_group"] == "default_group"
    
    def test_registry_event_consumer_service_deleted(self, db_session, base_daemon, 
                                                     daemon_repo, mock_storage_provider, 
                                                     mock_deployer_client):
        """Test processing ServiceDeleted event."""
        # Update daemon to UP status
        daemon_repo.update_daemon_status(db_session, base_daemon.id, DaemonStatus.UP)
        db_session.commit()
        
        event = {
            "Records": [{
                "body": json.dumps({
                    "Message": json.dumps({
                        "blockchain_event": {
                            "name": "ServiceDeleted",
                            "data": {
                                "json_str": str({
                                    "orgId": base_daemon.org_id.encode(),
                                    "serviceId": base_daemon.service_id.encode(),
                                    "metadataURI": b"ipfs://metadata-uri"
                                })
                            }
                        }
                    })
                })
            }]
        }
        
        # Mock tar file processing
        with patch('deployer.application.services.job_services.JobService._get_service_class') as mock_class:
            mock_class.return_value = "test.ServiceClass"
            
            response = job_handlers.registry_event_consumer(event, context=None)
        
        assert response == {}
        
        # Verify daemon updated
        daemon = daemon_repo.get_daemon(db_session, base_daemon.id)
        assert daemon.service_published is False
        
        # Verify stop daemon called
        mock_deployer_client.stop_daemon.assert_called_once_with(base_daemon.id)
    
    def test_check_daemons(self, db_session, base_daemon, daemon_repo, mock_deployer_client):
        """Test checking daemons status."""
        # Create multiple daemons with different statuses
        daemon2_data = TestDataFactory.create_daemon_data(
            daemon_id="daemon-2",
            status=DaemonStatus.UP
        )
        daemon_repo.create_daemon(db_session, daemon2_data)
        
        daemon3_data = TestDataFactory.create_daemon_data(
            daemon_id="daemon-3",
            status=DaemonStatus.STARTING
        )
        daemon_repo.create_daemon(db_session, daemon3_data)
        
        db_session.commit()
        
        response = job_handlers.check_daemons({}, None)
        
        assert response == {}
        
        # Verify update_daemon_status called for non-INIT/ERROR/DOWN daemons
        assert mock_deployer_client.update_daemon_status.call_count == 2
    
    def test_update_daemon_status(self, db_session, create_lambda_event, base_daemon, 
                                  daemon_repo, mock_haas_client):
        """Test updating daemon status based on HaaS check."""
        # Set daemon to STARTING
        daemon_repo.update_daemon_status(db_session, base_daemon.id, DaemonStatus.STARTING)
        db_session.commit()
        
        # Mock HaaS returns UP
        mock_haas_client.check_daemon.return_value = ("UP", datetime.now(UTC))
        
        event = create_lambda_event(
            path_params={"daemonId": base_daemon.id}
        )
        
        response = job_handlers.update_daemon_status(event, context=None)
        
        assert response == {}
        
        # Verify daemon status updated to UP
        daemon = daemon_repo.get_daemon(db_session, base_daemon.id)
        assert daemon.status == DaemonStatus.UP
    
    @patch('deployer.application.services.job_services.JobService._get_token_contract')
    @patch('deployer.application.services.job_services.JobService._get_order_id_from_transaction')
    @patch('deployer.application.services.job_services.BlockChainUtil')
    def test_update_transaction_status(self, mock_blockchain, mock_get_order_id, mock_get_contract,
                                       db_session, base_order, test_data_factory,
                                       transaction_repo, order_repo):
        """Test updating transaction status from blockchain."""
        # Create transactions metadata
        metadata = test_data_factory.create_transactions_metadata()
        db_session.add(metadata)
        db_session.commit()
        
        # Mock blockchain responses
        mock_bc_instance = Mock()
        mock_blockchain.return_value = mock_bc_instance
        mock_bc_instance.get_current_block_no.return_value = 2000
        mock_bc_instance.web3_object = Mock()
        
        # Mock contract events
        mock_contract = Mock()
        mock_get_contract.return_value = mock_contract
        mock_filter = Mock()
        mock_contract.events.Transfer.createFilter.return_value = mock_filter
        
        # Mock transfer event
        mock_event = {
            "transactionHash": MagicMock(hex=lambda: "0xNewTxHash"),
            "args": {
                "from": "0xSender",
                "to": metadata.recipient
            }
        }
        mock_filter.get_all_entries.return_value = [mock_event]
        
        # Mock order ID extraction
        mock_get_order_id.return_value = base_order.id
        
        response = job_handlers.update_transaction_status({}, None)
        
        assert response == {}
        
        # Verify transaction created/updated
        new_tx = transaction_repo.get_transaction(db_session, "0xNewTxHash")
        assert new_tx is not None
        assert new_tx.status == EVMTransactionStatus.SUCCESS
        
        # Verify order status updated
        order = order_repo.get_order(db_session, base_order.id)
        assert order.status == OrderStatus.SUCCESS


class TestAuthorizationService:
    """Tests for authorization checks."""
    
    def test_forbidden_access_wrong_account(self, db_session, create_lambda_event, base_daemon):
        """Test forbidden access when account doesn't match."""
        event = create_lambda_event(
            path_params={"daemonId": base_daemon.id},
            headers={
                "Authorization": "Bearer test-token",
                "x-cognito-username": "wrong-account-456"
            }
        )
        
        response = daemon_handlers.get_service_daemon(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.FORBIDDEN
    
    def test_daemon_not_found(self, create_lambda_event):
        """Test daemon not found error."""
        event = create_lambda_event(
            path_params={"daemonId": "non-existent-daemon"}
        )
        
        response = daemon_handlers.get_service_daemon(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.FORBIDDEN


class TestErrorHandling:
    """Tests for error handling scenarios."""
    
    def test_invalid_service_auth_parameters(self, create_lambda_event):
        """Test invalid service authentication parameters."""
        event = create_lambda_event(
            method="POST",
            body={
                "orgId": "test-org",
                "serviceId": "test-service",
                "serviceEndpoint": "https://endpoint.com",
                "serviceCredentials": [{"key": "API_KEY"}]  # Missing value and location
            }
        )
        
        response = order_handlers.initiate_order(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
        body = json.loads(response["body"])
        assert "Invalid service auth parameters" in body["error"]["message"]
    
    def test_claiming_not_available_wrong_status(self, db_session, create_lambda_event, 
                                                 base_daemon, daemon_repo):
        """Test claiming not available when daemon is not DOWN."""
        # Daemon is in INIT status by default
        event = create_lambda_event(
            path_params={"daemonId": base_daemon.id}
        )
        
        response = daemon_handlers.start_daemon_for_claiming(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
        body = json.loads(response["body"])
        assert "only available for DOWN status" in body["error"]["message"]
    
    def test_top_up_not_available_wrong_status(self, db_session, create_lambda_event, 
                                               base_daemon, daemon_repo):
        """Test top-up not available when daemon is in wrong status."""
        # Update daemon to STARTING status
        daemon_repo.update_daemon_status(db_session, base_daemon.id, DaemonStatus.STARTING)
        db_session.commit()
        
        event = create_lambda_event(
            method="POST",
            body={
                "orgId": base_daemon.org_id,
                "serviceId": base_daemon.service_id
            }
        )
        
        response = order_handlers.initiate_order(event, context=None)
        
        assert response["statusCode"] == HTTPStatus.BAD_REQUEST
        body = json.loads(response["body"])
        assert "only available only for UP, DOWN and READY_TO_START" in body["error"]["message"]