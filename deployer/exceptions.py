from common.exceptions import BadRequestException


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


class DaemonNotFoundForServiceException(BadRequestException):
    def __init__(self, org_id: str, service_id: str):
        super().__init__(
            message=f"Daemon for service with org_id={org_id} and service_id={service_id} not found!"
        )


class MissingServiceEndpointException(BadRequestException):
    def __init__(self):
        super().__init__(message="Missing service endpoint!")


class UpdateConfigNotAvailableException(BadRequestException):
    def __init__(self):
        super().__init__(message="Config update is not available!")


class MissingGithubParametersException(BadRequestException):
    def __init__(self):
        super().__init__(message="Missing github account name or repository name!")


class MissingCommitHashParameter(BadRequestException):
    def __init__(self):
        super().__init__(message="Missing commit hash parameter!")


class OrderNotFoundException(BadRequestException):
    def __init__(self, order_id: str):
        super().__init__(message=f"Order with id {order_id} not found!")


class UnacceptableOrderStatusException(BadRequestException):
    def __init__(self, status: str):
        super().__init__(message=f"Order status {status} is not acceptable for this operation!")


class DaemonAlreadyExistsException(BadRequestException):
    def __init__(self, org_id: str, service_id: str):
        super().__init__(
            message=f"Daemon for service with org_id={org_id} and service_id={service_id} already exists!"
        )


class HostedServiceNotFoundException(BadRequestException):
    def __init__(self, hosted_service_id: str = None, org_id: str = None, service_id: str = None):
        if org_id and service_id:
            super().__init__(
                message=f"Hosted service for service with org_id={org_id} and service_id={service_id} not found!"
            )
        elif hosted_service_id:
            super().__init__(message=f"Hosted service with id={hosted_service_id} not found!")
