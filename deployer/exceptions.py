from common.exceptions import BadRequestException


class InvalidDaemonStorageTypeParameter(BadRequestException):
    def __init__(self):
        super().__init__(message = "Invalid daemon storage type parameter")


class MissingServiceEventParameters(BadRequestException):
    def __init__(self):
        super().__init__(message = "Missing service event parameters: serviceId and/or metadataUri")