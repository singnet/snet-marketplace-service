from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any, Dict


@dataclass(slots=True)
class CustomException(Exception):
    http_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    code: int = 0
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[code {self.code}] {self.message}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }

class BadRequestException(CustomException):
    def __init__(self, message: str = "", details: Dict[str, Any] | None = None) -> None:
        super().__init__(
            http_code=HTTPStatus.BAD_REQUEST,
            message=message,
            details=details or {}
        )


class ForbiddenException(CustomException):
    def __init__(self):
        super().__init__(
            http_code=HTTPStatus.FORBIDDEN,
            message="Access denied"
        )


class ContentTypeNotSupportedException(CustomException):
    def __init__(self):
        super().__init__(
            http_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            message="Content type is not supported"
        )


class FailedResponse(CustomException):
    def __init__(self, code: int, message: str, details: Dict[str, Any] | None = None):
        super().__init__(
            http_code=HTTPStatus.BAD_REQUEST,
            code=code,
            message=message,
            details=details or {}
        )


class MethodNotImplemented(CustomException):
    def __init__(self, details: Dict[str, Any] | None = None):
        super().__init__(
            http_code=HTTPStatus.NOT_IMPLEMENTED,
            code=1001,
            message="Method not implemented",
            details=details or {}
        )


class OperationNotAllowed(CustomException):
    def __init__(self, details: Dict[str, Any] | None = None):
        super().__init__(
            http_code=HTTPStatus.FORBIDDEN,
            code=1002,
            message="Operation not allowed",
            details=details or {}
        )


class BadGateway(CustomException):
    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        super().__init__(
            http_code=HTTPStatus.BAD_GATEWAY,
            message=message,
            details=details or {}, 
        )


class InvalidFilePath(CustomException):
    def __init__(self, file_path: str | None = None):
        super().__init__(message=f"File not found in path {file_path}")


class TooLargeFileException(BadRequestException):
    def __init__(self):
        super().__init__(message="Too large file")


class LighthouseInternalException(BadRequestException):
    def __init__(self):
        super().__init__(message="Lighthouse internal exception")


class WrongTokenSymbolException(BadRequestException):
    def __init__(self):
        super().__init__(message="Wrong token symbol")


EXCEPTIONS_IGNORING_ALERT: tuple[type[CustomException], ...] = (FailedResponse,)
