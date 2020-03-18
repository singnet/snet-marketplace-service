from common.exceptions import CustomException


class BadRequestException(Exception):
    pass


class InvalidCallerReferenceException(CustomException):
    error_message = "INVALID CALLER REFERENCE"

    def __init__(self):
        super().__init__({})


class UserAlreadyExistException(CustomException):
    error_message = "USER ALREADY EXIST"

    def __init__(self):
        super().__init__({})


class EmailNotVerifiedException(CustomException):
    error_message = "EMAIL VERIFICATION PENDING"

    def __init__(self):
        super().__init__({})
