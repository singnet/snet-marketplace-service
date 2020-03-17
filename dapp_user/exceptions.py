from common.exceptions import CustomException


class BadRequestException(Exception):
    pass


class InvalidCallerReferenceException(CustomException):
    error_message = "INVALID CALLER REFERENCE"

    def __init__(self):
        super().__init__({})
