"""
Integration tests for update_transaction_status handler.

This handler updates the status of EVM transactions by checking their blockchain status.
"""
from datetime import datetime, UTC
from dateutil.relativedelta import relativedelta
from unittest.mock import patch, MagicMock
from sqlalchemy import select, text

from deployer.application.handlers.job_handlers import update_transaction_status
from deployer.infrastructure.models import EVMTransactionStatus, OrderStatus, DaemonStatus, TransactionsMetadata, EVMTransaction
from deployer.config import HAAS_FIX_PRICE_IN_COGS


class TestUpdateTransactionStatusHandler:
    """Test cases for update_transaction_status handler."""

    def test_update_transaction_status_success_from_blockchain(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo,
        transaction_repo
    ):
        """Test successful update of transaction status from blockchain events."""
        # Arrange
        # Create daemon with DOWN status (will be updated to READY_TO_START after payment)
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-update-tx-001",
            account_id="test-user-id-123",
            org_id="test-org",
            service_id="test-service",
            status=DaemonStatus.DOWN,
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Publish daemon
        test_data_factory.publish_daemon(db_session, "test-daemon-update-tx-001")
        
        order = test_data_factory.create_order(
            order_id="test-order-update-tx-001",
            daemon_id=daemon.id,
            status=OrderStatus.PROCESSING
        )
        order_repo.create_order(db_session, order)
        db_session.commit()
        
        # Create transaction metadata for blockchain polling directly in DB
        tx_metadata = TransactionsMetadata(
            recipient="0xRecipientAddress",
            last_block_no=1000,
            block_adjustment=1,
            fetch_limit=100
        )
        db_session.add(tx_metadata)
        db_session.commit()
        
        # Mock blockchain interactions and config for realistic test
        with patch("deployer.application.services.job_services.BlockChainUtil") as mock_bc_util_class, \
             patch("deployer.application.services.job_services.JobService._get_token_contract") as mock_get_contract, \
             patch("deployer.application.services.job_services.DAEMON_RUNNING_TIME_FOR_PRICE", {"months": 1}):
            
            # Setup blockchain mock
            mock_bc_instance = MagicMock()
            mock_bc_util_class.return_value = mock_bc_instance
            mock_bc_instance.get_current_block_no.return_value = 1200
            
            # Setup Web3 mock
            mock_w3 = MagicMock()
            mock_bc_instance.web3_object = mock_w3
            
            # Mock transaction details
            mock_transaction = {
                "input": bytes.fromhex("a9059cbb" + "0" * 128 + "test-order-update-tx-001".encode().hex().ljust(64, '0'))
            }
            mock_w3.eth.get_transaction.return_value = mock_transaction
            
            # Setup contract mock
            mock_contract = MagicMock()
            mock_get_contract.return_value = mock_contract
            
            # Mock Transfer events from blockchain
            mock_event = MagicMock()
            mock_event.__getitem__.side_effect = lambda key: {
                "transactionHash": MagicMock(hex=lambda: "0xabc123"),
                "args": {
                    "from": "0xSenderAddress",
                    "to": "0xRecipientAddress",
                    "value": HAAS_FIX_PRICE_IN_COGS
                }
            }[key]
            
            mock_filter = MagicMock()
            mock_filter.get_all_entries.return_value = [mock_event]
            mock_contract.events.Transfer.create_filter.return_value = mock_filter
            
            # Act
            response = update_transaction_status({}, lambda_context)
            
            # Assert
            assert response == {}  # Handler returns empty dict on success
            
            # Verify transaction was created in DB
            query = select(EVMTransaction).where(EVMTransaction.order_id == order.id)
            transactions = db_session.execute(query).scalars().all()
            assert len(transactions) > 0
            assert transactions[0].status == EVMTransactionStatus.SUCCESS
            
            # Verify order status was updated to SUCCESS
            updated_order = order_repo.get_order(db_session, order.id)
            assert updated_order.status == OrderStatus.SUCCESS
            
            # Verify daemon status was updated to READY_TO_START
            updated_daemon = daemon_repo.get_daemon(db_session, daemon.id)
            assert updated_daemon.status == DaemonStatus.READY_TO_START
            
            # Verify daemon end_at was set to new date (approximately 1 month from now)
            # Note: end_at from DB is naive datetime
            expected_end_at = datetime.now(UTC).replace(tzinfo=None) + relativedelta(months=1)
            assert updated_daemon.end_at.date() == expected_end_at.date()

    def test_update_transaction_status_extends_running_daemon(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo,
        transaction_repo
    ):
        """Test that successful transaction extends end_at for already running daemon."""
        # Arrange
        # Create daemon with UP status
        original_end_at = datetime.now(UTC) + relativedelta(days=5)
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-update-tx-002",
            status=DaemonStatus.UP,
            service_published=True,
            end_at=original_end_at
        )
        daemon_repo.create_daemon(db_session, daemon)
        
        # Publish daemon
        db_session.commit()
        test_data_factory.publish_daemon(db_session, "test-daemon-update-tx-002")
        
        order = test_data_factory.create_order(
            order_id="test-order-update-tx-002",
            daemon_id=daemon.id,
            status=OrderStatus.PROCESSING
        )
        order_repo.create_order(db_session, order)
        db_session.commit()
        
        # Create transaction metadata directly in DB
        tx_metadata = TransactionsMetadata(
            recipient="0xRecipientAddress2",
            last_block_no=2000,
            block_adjustment=1,
            fetch_limit=100
        )
        db_session.add(tx_metadata)
        db_session.commit()
        
        # Mock blockchain interactions and config for realistic test
        with patch("deployer.application.services.job_services.BlockChainUtil") as mock_bc_util_class, \
             patch("deployer.application.services.job_services.JobService._get_token_contract") as mock_get_contract, \
             patch("deployer.application.services.job_services.DAEMON_RUNNING_TIME_FOR_PRICE", {"months": 1}):
            
            # Setup blockchain mock
            mock_bc_instance = MagicMock()
            mock_bc_util_class.return_value = mock_bc_instance
            mock_bc_instance.get_current_block_no.return_value = 2200
            
            # Setup Web3 mock
            mock_w3 = MagicMock()
            mock_bc_instance.web3_object = mock_w3
            
            # Mock transaction details
            mock_transaction = {
                "input": bytes.fromhex("a9059cbb" + "0" * 128 + "test-order-update-tx-002".encode().hex().ljust(64, '0'))
            }
            mock_w3.eth.get_transaction.return_value = mock_transaction
            
            # Setup contract mock
            mock_contract = MagicMock()
            mock_get_contract.return_value = mock_contract
            
            # Mock Transfer event
            mock_event = MagicMock()
            mock_event.__getitem__.side_effect = lambda key: {
                "transactionHash": MagicMock(hex=lambda: "0xdef456"),
                "args": {
                    "from": "0xSenderAddress2",
                    "to": "0xRecipientAddress2",
                    "value": HAAS_FIX_PRICE_IN_COGS
                }
            }[key]
            
            mock_filter = MagicMock()
            mock_filter.get_all_entries.return_value = [mock_event]
            mock_contract.events.Transfer.create_filter.return_value = mock_filter
            
            # Act
            response = update_transaction_status({}, lambda_context)
            
            # Assert
            assert response == {}
            
            # Verify daemon status remains UP (daemon is already running)
            updated_daemon = daemon_repo.get_daemon(db_session, daemon.id)

            # For already running daemon (UP status), service_published stays True
            # and status stays UP - only end_at is extended
            assert updated_daemon.service_published is True
            assert updated_daemon.status == DaemonStatus.UP

            # end_at is extended by DAEMON_RUNNING_TIME_FOR_PRICE (1 month) from original end_at
            # Original was 5 days from now, so new should be ~5 days + 1 month from now
            expected_end_at = original_end_at.replace(tzinfo=None) + relativedelta(months=1)
            assert updated_daemon.end_at.date() == expected_end_at.date()




    def test_update_transaction_status_fails_old_transactions(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo,
        transaction_repo
    ):
        """Test that old pending transactions are marked as failed."""
        # Arrange
        daemon = test_data_factory.create_daemon()
        daemon_repo.create_daemon(db_session, daemon)
        
        order = test_data_factory.create_order(
            order_id="test-order-old",
            daemon_id=daemon.id,
            status=OrderStatus.PROCESSING
        )
        order_repo.create_order(db_session, order)
        
        # Create old pending transaction (will be failed by fail_old_transactions)
        old_transaction = test_data_factory.create_transaction(
            hash="0xold1234567890",
            order_id=order.id,
            status=EVMTransactionStatus.PENDING
        )
        transaction_repo.upsert_transaction(db_session, old_transaction)
        
        # Manually update created_at to make it old
        db_session.execute(
            text("UPDATE evm_transaction SET created_at = DATE_SUB(NOW(), INTERVAL 2 DAY) WHERE hash = :hash"),
            {"hash": old_transaction.hash}
        )
        db_session.commit()
        
        # Create transaction metadata (needed for update_transaction_status)
        tx_metadata = TransactionsMetadata(
            recipient="0xDefaultAddress",
            last_block_no=1000,
            block_adjustment=1,
            fetch_limit=100
        )
        db_session.add(tx_metadata)
        db_session.commit()
        
        # Mock empty blockchain results
        with patch("deployer.application.services.job_services.BlockChainUtil") as mock_bc_util_class, \
             patch("deployer.application.services.job_services.JobService._get_token_contract") as mock_get_contract:
            
            mock_bc_instance = MagicMock()
            mock_bc_util_class.return_value = mock_bc_instance
            mock_bc_instance.get_current_block_no.return_value = 1000
            
            mock_contract = MagicMock()
            mock_get_contract.return_value = mock_contract
            
            mock_filter = MagicMock()
            mock_filter.get_all_entries.return_value = []  # No new transactions
            mock_contract.events.Transfer.create_filter.return_value = mock_filter
            
            # Act
            response = update_transaction_status({}, lambda_context)
            
            # Assert
            assert response == {}
            
            # Verify old transaction was marked as failed
            updated_tx = transaction_repo.get_transaction(db_session, old_transaction.hash)
            assert updated_tx.status == EVMTransactionStatus.FAILED
            
            # Verify old order was marked as failed
            updated_order = order_repo.get_order(db_session, order.id)
            assert updated_order.status == OrderStatus.FAILED
