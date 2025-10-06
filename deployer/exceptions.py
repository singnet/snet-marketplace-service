from typing import Literal

from common.exceptions import BadRequestException
from deployer.constant import PeriodType


class InvalidServiceAuthParameters(BadRequestException):
    def __init__(self):
        super().__init__(
            message="Invalid service auth parameters! Must be 'key', 'value' and 'location' and not empty."
        )


class MissingServiceEventParameters(BadRequestException):
    def __init__(self):
        super().__init__(message="Missing service event parameters: serviceId and/or metadataUri!")


class DaemonNotFoundException(BadRequestException):
    def __init__(self, daemon_id: str):
        super().__init__(message=f"Daemon with id {daemon_id} not found!")


class MissingServiceEndpointException(BadRequestException):
    def __init__(self):
        super().__init__(message="Missing service endpoint!")


class ClaimingNotAvailableException(BadRequestException):
    def __init__(self, reason: Literal["status", "time"], last_claimed_at: str = ""):
        if reason == "status":
            super().__init__(message="Claiming is only available for DOWN status!")
        elif reason == "time":
            super().__init__(
                message=f"Claiming is only available 23 hours after the last claiming {last_claimed_at}!"
            )


class UpdateConfigNotAvailableException(BadRequestException):
    def __init__(self):
        super().__init__(message="Config update is not available!")


class TopUpNotAvailableException(BadRequestException):
    def __init__(self):
        super().__init__(
            message="Top up is only available only for UP, DOWN and READY_TO_START statuses!"
        )


class InvalidPeriodParameter(BadRequestException):
    def __init__(self, actual_value: str):
        super().__init__(message=f"Invalid period parameter! Actual value: {actual_value}. Expected one of {", ".join(PeriodType)}.")


class MissingGithubUrlException(BadRequestException):
    def __init__(self):
        super().__init__(message="Missing github url!")


class InvalidHaasServiceStatusParameter(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid haas service status parameter!")


class MissingCommitHashParameter(BadRequestException):
    def __init__(self):
        super().__init__(message="Missing commit hash parameter!")


class InvalidOrderParameter(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid order parameter")


class InvalidTypeOfMovementParameter(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid type of movement parameter!")


class OrderNotFoundException(BadRequestException):
    def __init__(self, order_id: str):
        super().__init__(message=f"Order with id {order_id} not found!")


class UnacceptableOrderStatusException(BadRequestException):
    def __init__(self, status: str):
        super().__init__(message=f"Order status {status} is not acceptable for this operation!")


class DaemonAlreadyExistsException(BadRequestException):
    def __init__(self, org_id: str, service_id: str):
        super().__init__(message=f"Daemon for service with org_id={org_id} and service_id={service_id} already exists!")
