# tests/integration/test_check_daemons.py
import json
from unittest.mock import patch, MagicMock

from deployer.application.handlers.job_handlers import check_daemons


class TestCheckDaemonsHandler:
    """Handler-level tests for check_daemons."""

    def test_check_daemons_calls_service_and_returns_empty(self):
        """
        Happy path: handler should call JobService.check_daemons() once
        and return {} (the handler does not wrap success in a Lambda envelope).
        """
        with patch("deployer.application.handlers.job_handlers.JobService") as JobServiceMock:
            svc = MagicMock()
            JobServiceMock.return_value = svc

            resp = check_daemons(event={}, context=None)

            # На успехе хэндлер возвращает сырой {} (декоратор не оборачивает)
            assert resp == {}
            svc.check_daemons.assert_called_once_with()

    def test_check_daemons_service_error_is_wrapped_into_500(self):
        """
        If JobService.check_daemons() raises, the @exception_handler should
        convert it into a 500 response with an error payload.
        """
        from common.constant import StatusCode

        with patch("deployer.application.handlers.job_handlers.JobService") as JobServiceMock:
            svc = MagicMock()
            svc.check_daemons.side_effect = RuntimeError("boom")
            JobServiceMock.return_value = svc

            resp = check_daemons(event={}, context=None)

            assert isinstance(resp, dict)
            assert resp["statusCode"] == StatusCode.INTERNAL_SERVER_ERROR

            body = json.loads(resp["body"])
            assert body.get("status") in ("failed", "error")
            assert "error" in body
