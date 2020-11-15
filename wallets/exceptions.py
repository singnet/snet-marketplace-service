from common.exceptions import CustomException, MethodNotImplemented, OperationNotAllowed


class BadRequestException(CustomException):
    error_message = "BAD_REQUEST"

    def __init__(self):
        super().__init__({})


EXCEPTIONS = (BadRequestException,)
