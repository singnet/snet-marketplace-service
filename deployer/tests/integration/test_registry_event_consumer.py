"""
Integration tests for registry_event_consumer handler.

This handler processes blockchain events related to service registration changes.
"""
import json
from unittest.mock import patch, MagicMock
from web3 import Web3

from deployer.application.handlers.job_handlers import registry_event_consumer
from deployer.infrastructure.models import DaemonStatus
from common.exceptions import BadRequestException
import pytest
import io
import tarfile

def _make_sns_sqs_event(blockchain_events):
    """
    Build an AWS event with SQS/SNS-like shape expected by get_events_from_queue():
    Records[n].body -> {"Message": "<json string>"}
    where the JSON string contains {"blockchain_event": <event>}.
    """
    records = []
    for ev in blockchain_events:
        message_str = json.dumps({"blockchain_event": ev})
        records.append({"body": json.dumps({"Message": message_str})})
    return {"Records": records}


def _be(name, org, service=None, meta=None):
    """
    Helper to create a single blockchain_event the way RegistryEventConsumerRequest expects.
    IMPORTANT:
      convert_data_types() will call Web3.to_text(value) on all fields except 'name',
      so here we must provide hex-encoded strings using Web3.to_hex(text=...).
    Also convert_data() uses ast.literal_eval on data['json_str'], so we pass a Python-literal string.
    """
    payload = {"orgId": Web3.to_hex(text=org)}
    if service is not None:
        payload["serviceId"] = Web3.to_hex(text=service)
    if meta is not None:
        payload["metadataURI"] = Web3.to_hex(text=meta)

    return {
        "name": name,
        "data": {
            # ast.literal_eval expects a Python-literal dict string (single quotes are fine)
            "json_str": str(payload)
        },
    }

# helper: build a valid in-memory tar with a .proto file
def _make_proto_tar_bytes(filename: str = "test.proto", text: str = "package test.service;\n") -> bytes:
    """Return a valid tar archive (as bytes) that contains a .proto file with given content."""
    content = text.encode("utf-8")
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        info = tarfile.TarInfo(name=filename)
        info.size = len(content)
        tar.addfile(tarinfo=info, fileobj=io.BytesIO(content))
    return buf.getvalue()

class TestRegistryEventConsumerHandler:
    """Test cases for registry_event_consumer handler."""

    def test_processes_service_created_event(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo
    ):
        """Test processing ServiceCreated event updates daemon configuration."""

        proto_tar_bytes = _make_proto_tar_bytes(text="package test.service;\n")

        # Arrange: existing daemon for the service
        daemon = test_data_factory.create_daemon(
            daemon_id="daemon-registry-001",
            org_id="org1",
            service_id="svc1",
            status=DaemonStatus.DOWN,
            service_published=False,  # Will be set to True by ServiceCreated
            daemon_endpoint="https://haas.singularitynet.io/org1/svc1",
            daemon_config={
                "payment_channel_storage_type": "etcd",
                "service_endpoint": "https://old-endpoint.com"
            }
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()

        # Event: ServiceCreated
        event = _make_sns_sqs_event([
            _be("ServiceCreated", org="org1", service="svc1", meta="ipfs://meta1")
        ])

        # Mock storage provider to return metadata and a valid tar for service_api_source
        with patch("deployer.application.services.job_services.StorageProvider") as mock_storage_class:
            mock_storage = MagicMock()
            mock_storage_class.return_value = mock_storage

            def _mock_get(uri, to_decode=True):
                if uri == "ipfs://meta1":
                    return {
                        "groups": [{
                            "group_name": "default-group",
                            "endpoints": ["https://haas.singularitynet.io/org1/svc1"]
                        }],
                        "service_api_source": "ipfs://service-api-tar"
                    }
                # return a valid tar archive with a .proto containing `package ...;`
                return proto_tar_bytes

            mock_storage.get.side_effect = _mock_get

            # Act
            response = registry_event_consumer(event, lambda_context)

            # Assert
            assert response == {}  # Handler returns empty dict on success

            # Verify daemon was updated
            updated_daemon = daemon_repo.get_daemon(db_session, "daemon-registry-001")
            assert updated_daemon.service_published is True  # ServiceCreated sets this to True
            assert updated_daemon.daemon_config["daemon_group"] == "default-group"

            assert "service_class" in updated_daemon.daemon_config
            assert updated_daemon.daemon_config["service_class"] == "test.service"

            # Verify storage provider calls
            mock_storage.get.assert_any_call("ipfs://meta1")
            mock_storage.get.assert_any_call("ipfs://service-api-tar", to_decode=False)


    def test_processes_service_metadata_modified_triggers_redeploy(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo
    ):
        """Test ServiceMetadataModified event triggers daemon redeploy when daemon is UP."""


        proto_tar_bytes_v2 = _make_proto_tar_bytes(text="package test.service.v2;\n")

        # Arrange: existing daemon in UP status
        daemon = test_data_factory.create_daemon(
            daemon_id="daemon-registry-002",
            org_id="org2",
            service_id="svc2",
            status=DaemonStatus.UP,  # Daemon is running
            service_published=True,
            daemon_endpoint="https://haas.singularitynet.io/org2/svc2",
            daemon_config={
                "payment_channel_storage_type": "etcd",
                "daemon_group": "old-group"
            }
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()

        # Event: ServiceMetadataModified
        event = _make_sns_sqs_event([
            _be("ServiceMetadataModified", org="org2", service="svc2", meta="ipfs://meta2")
        ])

        # Mock storage provider and deployer client
        with patch("deployer.application.services.job_services.StorageProvider") as mock_storage_class, \
            patch("deployer.application.services.job_services.DeployerClient") as mock_deployer_class:

            mock_storage = MagicMock()
            mock_storage_class.return_value = mock_storage

            mock_deployer = MagicMock()
            mock_deployer_class.return_value = mock_deployer

            # Return updated metadata and a valid tar for service_api_source
            def _mock_get(uri, to_decode=True):
                if uri == "ipfs://meta2":
                    return {
                        "groups": [{
                            "group_name": "new-group",
                            "endpoints": ["https://haas.singularitynet.io/org2/svc2"]
                        }],
                        "service_api_source": "ipfs://service-api-tar-v2"
                    }
                # Return a valid tar archive (bytes) for the service API
                return proto_tar_bytes_v2

            mock_storage.get.side_effect = _mock_get

            # Act
            response = registry_event_consumer(event, lambda_context)

            # Assert
            assert response == {}

            updated_daemon = daemon_repo.get_daemon(db_session, "daemon-registry-002")
            assert updated_daemon.daemon_config["daemon_group"] == "new-group"
            assert "service_class" in updated_daemon.daemon_config
            assert updated_daemon.daemon_config["service_class"] == "test.service.v2"

            mock_deployer.redeploy_daemon.assert_called_once_with("daemon-registry-002")
            mock_storage.get.assert_any_call("ipfs://meta2")
            mock_storage.get.assert_any_call("ipfs://service-api-tar-v2", to_decode=False)


    def test_processes_service_deleted_stops_daemon(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo
    ):
        """Test ServiceDeleted event sets service_published to False and stops daemon if UP."""
        # Build a valid tar for service_api_source
        proto_tar_bytes = _make_proto_tar_bytes(text="package test.service;\n")

        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="daemon-registry-003",
            org_id="org3",
            service_id="svc3",
            status=DaemonStatus.UP,  # Daemon is running
            service_published=True,
            daemon_endpoint="https://haas.singularitynet.io/org3/svc3",
            daemon_config={"payment_channel_storage_type": "etcd"}
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()

        # Create ServiceDeleted event
        event = _make_sns_sqs_event([
            _be("ServiceDeleted", org="org3", service="svc3", meta="ipfs://meta3")
        ])

        # Mock storage provider and deployer client
        with patch("deployer.application.services.job_services.StorageProvider") as mock_storage_class, \
            patch("deployer.application.services.job_services.DeployerClient") as mock_deployer_class:

            mock_storage = MagicMock()
            mock_storage_class.return_value = mock_storage

            mock_deployer = MagicMock()
            mock_deployer_class.return_value = mock_deployer

            # Return metadata and a valid tar for service_api_source
            def _mock_get(uri, to_decode=True):
                if uri == "ipfs://meta3":
                    return {
                        "groups": [{
                            "group_name": "default-group",
                            "endpoints": ["https://haas.singularitynet.io/org3/svc3"]
                        }],
                        "service_api_source": "ipfs://service-api-tar"
                    }
                # Return a valid tar archive (bytes) for the service API
                return proto_tar_bytes

            mock_storage.get.side_effect = _mock_get

            # Act
            response = registry_event_consumer(event, lambda_context)

            # Assert
            assert response == {}

            updated_daemon = daemon_repo.get_daemon(db_session, "daemon-registry-003")
            # ServiceDeleted should unpublish service
            assert updated_daemon.service_published is False
            # Redeploy must not be called for delete
            mock_deployer.redeploy_daemon.assert_not_called()
            # Stop must be called because daemon was UP
            mock_deployer.stop_daemon.assert_called_once_with("daemon-registry-003")

            # Optional: verify storage calls (including tar fetch with to_decode=False)
            mock_storage.get.assert_any_call("ipfs://meta3")
            mock_storage.get.assert_any_call("ipfs://service-api-tar", to_decode=False)


    def test_ignores_events_for_non_haas_services(
        self,
        lambda_context,
        db_session
    ):
        """Test that events for services not using HaaS are ignored."""
        # Arrange - No daemon exists for this org/service
        event = _make_sns_sqs_event([
            _be("ServiceCreated", org="non-haas-org", service="non-haas-svc", meta="ipfs://meta")
        ])
        
        # Mock storage provider (should not be called)
        with patch("deployer.application.services.job_services.StorageProvider") as mock_storage_class:
            mock_storage = MagicMock()
            mock_storage_class.return_value = mock_storage
            
            # Act
            response = registry_event_consumer(event, lambda_context)
            
            # Assert
            assert response == {}
            
            # Verify storage provider was NOT called (service doesn't use HaaS)
            mock_storage.get.assert_not_called()

    def test_stops_daemon_when_endpoint_changes(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo
    ):
        """Test that daemon is stopped when service endpoint changes (no longer using HaaS)."""
        # build a valid tar for service_api_source
        proto_tar_bytes = _make_proto_tar_bytes(text="package test.service;\n")

        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="daemon-registry-004",
            org_id="org4",
            service_id="svc4",
            status=DaemonStatus.UP,
            service_published=True,
            daemon_endpoint="https://haas.singularitynet.io/org4/svc4"
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()

        # Event with changed endpoint
        event = _make_sns_sqs_event([
            _be("ServiceMetadataModified", org="org4", service="svc4", meta="ipfs://meta4")
        ])

        # Mock storage provider and deployer client
        with patch("deployer.application.services.job_services.StorageProvider") as mock_storage_class, \
            patch("deployer.application.services.job_services.DeployerClient") as mock_deployer_class:

            mock_storage = MagicMock()
            mock_storage_class.return_value = mock_storage

            mock_deployer = MagicMock()
            mock_deployer_class.return_value = mock_deployer

            # Return metadata with non-HaaS endpoint and a valid tar for service_api_source
            def _mock_get(uri, to_decode=True):
                if uri == "ipfs://meta4":
                    return {
                        "groups": [{
                            "group_name": "default-group",
                            "endpoints": ["https://custom-endpoint.com"]  # not HaaS
                        }],
                        "service_api_source": "ipfs://service-api-tar"
                    }
                return proto_tar_bytes  # valid tar bytes

            mock_storage.get.side_effect = _mock_get

            # Act
            response = registry_event_consumer(event, lambda_context)

            # Assert
            assert response == {}
            mock_deployer.stop_daemon.assert_called_once_with("daemon-registry-004")
            mock_deployer.redeploy_daemon.assert_not_called()
            mock_storage.get.assert_any_call("ipfs://meta4")
            mock_storage.get.assert_any_call("ipfs://service-api-tar", to_decode=False)


    def test_invalid_event_raises_bad_request(
        self,
        lambda_context
    ):
        """Test that invalid event structure raises BadRequestException."""
        # Arrange - ServiceCreated without required fields
        event = _make_sns_sqs_event([
            _be("ServiceCreated", org="org1")  # Missing service and metadata
        ])
        
        # Act & Assert
        with pytest.raises(BadRequestException):
            registry_event_consumer(event, lambda_context)
