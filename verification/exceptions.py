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


EXCEPTIONS = (UnableToInitiateException, BadRequestException, NotAllowedToInitiateException,
              InvalidSlackChannelException, InvalidSlackUserException, InvalidSlackSignatureException)
