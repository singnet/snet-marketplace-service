from common.exceptions import (
    BadRequestException,
    MethodNotImplemented,
    OperationNotAllowed,
)


class OrganizationNotFoundException(BadRequestException):
    def __init__(self):
        super().__init__(message="Bad request exception")


class InvalidOriginException(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid origin")


class InvalidOrganizationStateException(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid organization state")


class InvalidMetadataException(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid metadata")


class InvalidServiceStateException(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid service state")


class ServiceProtoNotFoundException(BadRequestException):
    def __init__(self):
        super().__init__(message="Service proto not found")


class InvalidOrganizationType(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid Organization type")


class OrganizationNotPublishedException(BadRequestException):
    def __init__(self):
        super().__init__(message="Organization is not published")


class ServiceNotFoundException(BadRequestException):
    def __init__(self):
        super().__init__(message="Service not found")


class ServiceGroupNotFoundException(BadRequestException):
    def __init__(self):
        super().__init__(message="Service group not found")


class EnvironmentNotFoundException(BadRequestException):
    def __init__(self):
        super().__init__(message="Environmet not found")


class InvalidSlackUserException(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid slack user")


class InvalidSlackChannelException(BadRequestException):
    def __init__(self):
        super().__init__(message="Slack channel not allowed")


class InvalidSlackSignatureException(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid slack signature")


class InvalidFileTypeException(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid file type")


class FileNotFoundException(BadRequestException):
    def __init__(self):
        super().__init__(message="File not found")


class NewMemberAddressException(BadRequestException):
    def __init__(self):
        super().__init__(message="New member address equals owner address")

EXCEPTIONS = (BadRequestException, OrganizationNotFoundException, InvalidOriginException, MethodNotImplemented,
              InvalidOrganizationStateException, InvalidMetadataException, InvalidServiceStateException,
              ServiceProtoNotFoundException, OrganizationNotPublishedException,
              ServiceNotFoundException, ServiceGroupNotFoundException, EnvironmentNotFoundException,
              InvalidSlackUserException, InvalidSlackChannelException, InvalidSlackSignatureException,
              InvalidFileTypeException, FileNotFoundException, OperationNotAllowed, InvalidOrganizationType,
              NewMemberAddressException)
