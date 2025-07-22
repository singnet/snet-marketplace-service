from common.exceptions import BadRequestException


class InvalidContentType(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid content type")


class ProtoNotFound(BadRequestException):
    def __init__(self):
        super().__init__(message="Proto file not nound")


class InvalidUploadType(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid upload type")


class EmptyFileException(BadRequestException):
    def __init__(self):
        super().__init__(message="Empty file")


class MissingUploadTypeDetailsParams(BadRequestException):
    def __init__(self):
        super().__init__(message="Missing required parameters: org_uuid and/or service_uuid")


EXCEPTIONS = (
    BadRequestException,
    InvalidContentType,
    ProtoNotFound,
    InvalidUploadType,
    EmptyFileException,
    MissingUploadTypeDetailsParams,
)
