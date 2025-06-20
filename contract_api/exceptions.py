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