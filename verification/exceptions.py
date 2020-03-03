from common.exceptions import CustomException


class BadRequestException(CustomException):
    error_message = "BAD_REQUEST"

    def __init__(self):
        super().__init__({})


class UnableToInitiateException(CustomException):
    error_message = "UNABLE_TO_INITIATE"

    def __init__(self):
        super().__init__({})


class NotAllowedToInitiateException(CustomException):
    error_message = "NOT_ALLOWED_TO_INITIATE"

    def __init__(self, message):
        super().__init__({
            "message": message
        })


EXCEPTIONS = (UnableToInitiateException, BadRequestException, NotAllowedToInitiateException)
