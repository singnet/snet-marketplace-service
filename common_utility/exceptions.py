from common.exceptions import CustomException


class BadRequestException(CustomException):
    error_message = "BAD_REQUEST"

    def __init__(self):
        super().__init__({})


class InvalidContentType(CustomException):
    error_message = "INVALID_CONTENT_TYPE"

    def __init__(self):
        super().__init__({})


EXCEPTIONS = (BadRequestException, InvalidContentType)
