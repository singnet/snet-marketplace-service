from common.exceptions import BadRequestException


class InvalidUpdatingChannelParameters(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid body parameters: signed_amount required for METAMASK wallet, "
                                 "org_id and service_id required for GENERAL wallet")


class MissingFilePathException(BadRequestException):
    def __init__(self):
        super().__init__(message="Missing file path in S3 event")


class InvalidSortParameter(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid sort parameter")


class InvalidOrderParameter(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid order parameter")


class InvalidFilterParameter(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid filter parameter")


class InvalidCurateParameter(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid curate parameter")


class InvalidAttributeParameter(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid attribute parameter")


class ChannelNotFoundException(BadRequestException):
    def __init__(self, channel_id: int):
        super().__init__(message=f"Channel with id {channel_id} not found")


class CreatingSignatureFailedException(BadRequestException):
    def __init__(self):
        super().__init__(message=f"Failed to create signature using signer service")


class DaemonInteractionFailedException(BadRequestException):
    def __init__(self):
        super().__init__(message="Daemon interaction failed")


class BuildTriggerFailedException(BadRequestException):
    def __init__(self):
        super().__init__(message="Build trigger failed")


class UpsertOffchainConfigsFailedException(BadRequestException):
    def __init__(self, org_id: str, service_id: str):
        super().__init__(message=f"Upsert offchain configs failed for {org_id} and {service_id}")


class ServiceCurationFailedException(BadRequestException):
    def __init__(self, org_id: str, service_id: str):
        super().__init__(message=f"Service curation failed for {org_id} and {service_id}")


class ServiceNotFoundException(BadRequestException):
    def __init__(self, org_id: str, service_id: str):
        super().__init__(message=f"Service not found for {org_id} and {service_id}")


class UpdateServiceRatingFailedException(BadRequestException):
    def __init__(self, org_id: str, service_id: str):
        super().__init__(message=f"Update service rating failed for {org_id} and {service_id}")

