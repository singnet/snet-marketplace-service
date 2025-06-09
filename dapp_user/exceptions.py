from common.exceptions import CustomException


class InvalidCallerReferenceException(CustomException):
    def __init__(self):
        super().__init__(message="Invalid caller reference")


class UserAlreadyExistException(CustomException):
    def __init__(self):
        super().__init__(message="User already exist")


class EmailNotVerifiedException(CustomException):
    def __init__(self):
        super().__init__(message="Email verification pending")
