from common.exceptions import (
    BadGateway,
    BadRequestException,
)


class ZeroFreeCallsAvailable(BadRequestException):
    """Raised when the user has zero available free calls."""

    def __init__(self) -> None:
        super().__init__(message="No free call tokens available.")


class DaemonUnavailable(BadGateway):
    """Raised when the daemon service is not responding."""

    def __init__(self) -> None:
        super().__init__(message="The daemon is not responding. Please contact the service owner.")
