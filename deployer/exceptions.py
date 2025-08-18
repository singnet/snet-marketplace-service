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