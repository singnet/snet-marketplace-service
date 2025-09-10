"""
Integration tests for save_evm_transaction handler.
"""
import json
import pytest

from deployer.application.handlers.transaction_handlers import save_evm_transaction
from deployer.infrastructure.models import OrderStatus, EVMTransactionStatus
from common.constant import StatusCode


class TestSaveEVMTransactionHandler:
    """Test cases for save_evm_transaction handler."""
    
    def test_save_evm_transaction_success_new(
        self,
        save_evm_transaction_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo,
        transaction_repo
    ):
        """Test successful saving of new EVM transaction."""
        # Arrange
        # Create daemon with correct account_id
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-tx-001",
            account_id="test-user-id-123",  # Matches authorized_event
            org_id="test-org",
            service_id="test-service"
        )
        daemon_repo.create_daemon(db_session, daemon)
        
        # Create order for this daemon
        order = test_data_factory.create_order(
            order_id="test-order-tx-001",
            daemon_id=daemon.id,
            status=OrderStatus.PROCESSING
        )
        order_repo.create_order(db_session, order)
        db_session.commit()
        
        # Prepare event
        event = save_evm_transaction_event.copy()
        event["body"] = json.dumps({
            "orderId": "test-order-tx-001",
            "transactionHash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "sender": "0xUserWalletAddress1234567890abcdef123456",
            "recipient": "0xMarketplaceAddress1234567890abcdef12345"
        })
        
        # Act
        response = save_evm_transaction(event, lambda_context)
        
        # Assert
        assert response["statusCode"] == StatusCode.OK
        
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["data"] == {}  # save_evm_transaction returns empty dict
        
        # Verify transaction was saved
        transaction = transaction_repo.get_transaction(
            db_session, 
            "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        )
        assert transaction is not None
        assert transaction.order_id == "test-order-tx-001"
        assert transaction.status == EVMTransactionStatus.PENDING
        assert transaction.sender == "0xUserWalletAddress1234567890abcdef123456"
        assert transaction.recipient == "0xMarketplaceAddress1234567890abcdef12345"
    
    def test_save_evm_transaction_success_update_existing(
        self,
        save_evm_transaction_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo,
        transaction_repo
    ):
        """Test successful updating of existing EVM transaction (upsert functionality)."""
        # Arrange
        # Create daemon and order
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-tx-002",
            account_id="test-user-id-123"
        )
        daemon_repo.create_daemon(db_session, daemon)
        
        order = test_data_factory.create_order(
            order_id="test-order-tx-002",
            daemon_id=daemon.id,
            status=OrderStatus.PROCESSING
        )
        order_repo.create_order(db_session, order)
        
        # Create existing transaction with FAILED status
        existing_tx_hash = "0xaabbccddaabbccddaabbccddaabbccddaabbccddaabbccddaabbccddaabbccdd"
        existing_transaction = test_data_factory.create_transaction(
            hash=existing_tx_hash,
            order_id="test-order-tx-002",
            status=EVMTransactionStatus.FAILED,
            sender="0xOldSender1234567890abcdef1234567890abcdef",
            recipient="0xOldRecipient1234567890abcdef1234567890ab"
        )
        transaction_repo.upsert_transaction(db_session, existing_transaction)
        db_session.commit()
        
        # Prepare event with same transaction hash (simulating retry)
        event = save_evm_transaction_event.copy()
        event["body"] = json.dumps({
            "orderId": "test-order-tx-002",
            "transactionHash": existing_tx_hash,
            "sender": "0xNewSender1234567890abcdef1234567890abcdef",
            "recipient": "0xNewRecipient1234567890abcdef1234567890ab"
        })
        
        # Act
        response = save_evm_transaction(event, lambda_context)
        
        # Assert
        assert response["statusCode"] == StatusCode.OK
        
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        # Verify transaction was updated (upserted)
        transaction = transaction_repo.get_transaction(db_session, existing_tx_hash)
        assert transaction is not None
        assert transaction.order_id == "test-order-tx-002"
        assert transaction.status == EVMTransactionStatus.PENDING  # Status updated to PENDING
        # Note: sender and recipient are NOT updated in upsert (only status is updated)
        assert transaction.sender == "0xOldSender1234567890abcdef1234567890abcdef"  # Unchanged
        assert transaction.recipient == "0xOldRecipient1234567890abcdef1234567890ab"  # Unchanged
