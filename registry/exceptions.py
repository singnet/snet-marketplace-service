from http import HTTPStatus
from common.exceptions import CustomException, MethodNotImplemented, OperationNotAllowed


class BadRequestException(CustomException):
    error_message = "BAD_REQUEST"

    def __init__(self):
        super().__init__({})


class OrganizationNotFoundException(CustomException):
    error_message = "ORGANIZATION_NOT_FOUND"

    def __init__(self):
        super().__init__({})


class InvalidOriginException(CustomException):
    error_message = "INVALID_ORIGIN"

    def __init__(self):
        super().__init__({})


class InvalidOrganizationStateException(CustomException):
    error_message = "INVALID_ORGANIZATION_STATE"

    def __init__(self):
        super().__init__({})


class InvalidMetadataException(CustomException):
    error_message = "INVALID_METADATA_EXCEPTION"

    def __init__(self):
        super().__init__({})


class InvalidServiceStateException(CustomException):
    error_message = "INVALID_SERVICE_STATE"

    def __init__(self):
        super().__init__({})


class ServiceProtoNotFoundException(CustomException):
    error_message = "SERVICE_PROTO_NOT_FOUND"

    def __init__(self):
        super().__init__({})


class InvalidOrganizationType(CustomException):
    error_message = "Invalid Organization Type"

    def __init__(self):
        super().__init__({})


class OrganizationNotPublishedException(CustomException):
    error_message = "ORGANIZATION IS NOT PUBLISHED"

    def __init__(self):
        super().__init__({})


class ServiceNotFoundException(CustomException):
    error_message = "SERVICE_NOT_FOUND"

    def __init__(self):
        super().__init__({})


class ServiceGroupNotFoundException(CustomException):
    error_message = "SERVICE_GROUP_NOT_FOUND"

    def __init__(self):
        super().__init__({})


class EnvironmentNotFoundException(CustomException):
    error_message = "Environment Not Found"

    def __init__(self):
        super().__init__({})


class InvalidSlackUserException(CustomException):
    error_message = "SLACK_USER"

    def __init__(self):
        super().__init__({})


class InvalidSlackChannelException(CustomException):
    error_message = "SLACK_CHANNEL_NOT_ALLOWED"

    def __init__(self):
        super().__init__({})


class InvalidSlackSignatureException(CustomException):
    error_message = "SLACK_SIGN_NOT_ALLOWED"

    def __init__(self):
        super().__init__({})


class InvalidFileTypeException(CustomException):
    error_message = "INVALID_FILE_TYPE_EXCEPTION"

    def __init__(self):
        super().__init__({})


class FileNotFoundException(CustomException):
    error_message = "FILE_NOT_FOUND"

    def __init__(self):
        super().__init__({})

class ForbiddenException(CustomException):
    error_message = "FORBIDDEN_ERROR"

    def __init__(self):
        super().__init__(
            http_code=HTTPStatus.FORBIDDEN
        )

class LighthouseInternalException(CustomException):
    error_message = "LIGHTHOUSE_INTERNAL_SERVER_ERROR"

    def __init__(self):
        super().__init__({})

EXCEPTIONS = (BadRequestException, OrganizationNotFoundException, InvalidOriginException, MethodNotImplemented,
              InvalidOrganizationStateException, InvalidMetadataException, InvalidServiceStateException,
              ServiceProtoNotFoundException, OrganizationNotPublishedException, ForbiddenException,
              ServiceNotFoundException, ServiceGroupNotFoundException, EnvironmentNotFoundException,
              InvalidSlackUserException, InvalidSlackChannelException, InvalidSlackSignatureException,
              InvalidFileTypeException, FileNotFoundException, OperationNotAllowed, InvalidOrganizationType,
              LighthouseInternalException)
