from common.exceptions import BadRequestException


class ZeroFreeCallsAvailable(BadRequestException):
    def __init__(self) -> None:
        super().__init__(message="Zero free calls token available")