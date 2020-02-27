from common.exceptions import CustomException


class BadRequestException(CustomException):
    error_message = "BAD_REQUEST"

    def __init__(self):
        super().__init__({})


class UnableToInitiateException(CustomException):
    error_message = "UNABLE_TO_INITIATE"

    def __init__(self):
        super().__init__({})
