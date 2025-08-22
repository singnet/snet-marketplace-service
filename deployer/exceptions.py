from typing import Union, Literal

from common.exceptions import BadRequestException


class InvalidServiceAuthParameters(BadRequestException):
    def __init__(self):
        super().__init__(message = "Invalid service auth parameters. Must be 'key', 'value' and 'location' and not empty.")


class MissingServiceEventParameters(BadRequestException):
    def __init__(self):
        super().__init__(message = "Missing service event parameters: serviceId and/or metadataUri")


class DaemonNotFoundException(BadRequestException):
    def __init__(self, daemon_id: str):
        super().__init__(message = f"Daemon with id {daemon_id} not found!")


class MissingServiceEndpointException(BadRequestException):
    def __init__(self):
        super().__init__(message = "Missing service endpoint")


class ClaimingNotAvailableException(BadRequestException):
    def __init__(self, reason: Literal["status", "time"], last_claimed_at: str = ""):
        if reason == "status":
            super().__init__(message = "Claiming is only available for DOWN status")
        elif reason == "time":
            super().__init__(message = f"Claiming is only available 23 hours after the last claiming {last_claimed_at}")


class UpdateConfigNotAvailableException(BadRequestException):
    def __init__(self):
        super().__init__(message = "Config update is unavailable during deploying the daemon")


class TopUpNotAvailableException(BadRequestException):
    def __init__(self):
        super().__init__(message = "Top up is only available only for UP, DOWN and READY_TO_START statuses")