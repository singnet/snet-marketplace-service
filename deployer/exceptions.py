from common.exceptions import BadRequestException


class InvalidServiceAuthParameters(BadRequestException):
    def __init__(self):
        super().__init__(message = "Invalid service auth parameters. Must be 'key', 'value' and 'location'")


class MissingServiceEventParameters(BadRequestException):
    def __init__(self):
        super().__init__(message = "Missing service event parameters: serviceId and/or metadataUri")