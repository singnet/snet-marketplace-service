from http import HTTPStatus

from common.exceptions import BadRequestException, CustomException


class UnauthorizedException(CustomException):
    def __init__(self):
        super().__init__(
            http_code=HTTPStatus.UNAUTHORIZED,
            message="You are not allowed to delete this user",
        )


class InvalidCallerReferenceException(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid caller reference")


class UserAlreadyExistException(BadRequestException):
    def __init__(self):
        super().__init__(message="User already exist")


class UserNotFoundHTTPException(BadRequestException):
    def __init__(self, username: str):
        super().__init__(message=f"User with username '{username}' not found")


class EmailNotVerifiedException(BadRequestException):
    def __init__(self):
        super().__init__(message="Email verification pending")
