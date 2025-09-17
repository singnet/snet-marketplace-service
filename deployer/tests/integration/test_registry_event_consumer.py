"""
Tests for registry_event_consumer handler.

We mock JobService at the import site of the handler to verify:
- allowed events trigger process_registry_event()
- unknown events are ignored
- no records -> nothing is called, handler returns {}
- invalid allowed event (missing required fields) is wrapped into BadRequestException by validation_handler
"""

import json
from unittest.mock import patch, MagicMock
import pytest
from web3 import Web3

from deployer.application.handlers.job_handlers import registry_event_consumer
from common.exceptions import BadRequestException


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


class TestRegistryEventConsumerHandler:
    def test_processes_allowed_events_and_skips_others(self):
        """
        Arrange: Created, MetadataModified, and an unknown RandomEvent.
        Assert: JobService.process_registry_event called exactly for the first two,
        with already-validated Pydantic models (decoded back from hex).
        """
        event = _make_sns_sqs_event(
            [
                _be("ServiceCreated", org="org1", service="svc1", meta="ipfs://meta1"),
                _be("ServiceMetadataModified", org="org2", service="svc2", meta="ipfs://meta2"),
                _be("RandomEvent", org="orgX"),  # unknown -> ignored by handler
            ]
        )

        with patch("deployer.application.handlers.job_handlers.JobService") as JobServiceMock:
            svc = MagicMock()
            JobServiceMock.return_value = svc

            resp = registry_event_consumer(event, context=None)

            # Handler returns {} (no lambda response envelope here)
            assert resp == {}

            # Only allowed events should trigger processing
            assert svc.process_registry_event.call_count == 2

            first_req = svc.process_registry_event.call_args_list[0].args[0]
            assert first_req.event_name == "ServiceCreated"
            assert first_req.org_id == "org1"
            assert first_req.service_id == "svc1"
            assert first_req.metadata_uri == "ipfs://meta1"

            second_req = svc.process_registry_event.call_args_list[1].args[0]
            assert second_req.event_name == "ServiceMetadataModified"
            assert second_req.org_id == "org2"
            assert second_req.service_id == "svc2"
            assert second_req.metadata_uri == "ipfs://meta2"

    def test_no_records_returns_empty_and_no_calls(self):
        """Empty Records array -> nothing to do, returns {} and does not call JobService."""
        event = {"Records": []}

        with patch("deployer.application.handlers.job_handlers.JobService") as JobServiceMock:
            svc = MagicMock()
            JobServiceMock.return_value = svc

            resp = registry_event_consumer(event, context=None)

            assert resp == {}
            svc.process_registry_event.assert_not_called()

    def test_invalid_allowed_event_raises(self):
        """
        Allowed event without required fields (serviceId/metadataURI) -> model validator fails.
        Because validate_event is wrapped in @validation_handler, the error is surfaced as BadRequestException.
        """
        event = _make_sns_sqs_event([_be("ServiceCreated", org="org1")])  # missing fields

        with patch("deployer.application.handlers.job_handlers.JobService") as JobServiceMock:
            JobServiceMock.return_value = MagicMock()
            with pytest.raises(BadRequestException):
                registry_event_consumer(event, context=None)
