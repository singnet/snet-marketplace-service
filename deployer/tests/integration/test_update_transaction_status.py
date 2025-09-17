import json
from unittest.mock import patch, MagicMock

from deployer.application.handlers.job_handlers import update_transaction_status
from common.constant import StatusCode


class TestUpdateTransactionStatusHandler:
    def test_update_tx_status_calls_service_and_returns_empty(self):
        """
        Handler should just call JobService.update_transaction_status() and return {}.
        We patch JobService in the handler module to isolate handler behavior.
        """
        with patch("deployer.application.handlers.job_handlers.JobService") as JobServiceMock:
            svc = MagicMock()
            JobServiceMock.return_value = svc

            resp = update_transaction_status(event={}, context=None)

            svc.update_transaction_status.assert_called_once_with()
            assert resp == {}  # handler itself returns empty dict on success

    def test_update_tx_status_service_error_is_wrapped_into_500(self):
        with patch("deployer.application.handlers.job_handlers.JobService") as JobServiceMock:
            svc = MagicMock()
            svc.update_transaction_status.side_effect = RuntimeError("boom")
            JobServiceMock.return_value = svc

            resp = update_transaction_status(event={}, context=None)

            assert isinstance(resp, dict)
            assert resp["statusCode"] == StatusCode.INTERNAL_SERVER_ERROR

            body = json.loads(resp["body"])
            assert body.get("status") in ("failed", "error")
            assert "error" in body

            # Error can be a string or a dict; just check it's present and non-empty
            err = body["error"]
            if isinstance(err, dict):
                # allow any non-empty message field
                assert err.get("message")
            else:
                assert isinstance(err, str) and err  # non-empty string

