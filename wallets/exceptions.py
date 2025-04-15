from common.exceptions import CustomException, MethodNotImplemented, OperationNotAllowed


class BadRequestException(CustomException):
    error_message = "BAD_REQUEST"

    def __init__(self, msg=None):
        super().__init__({"msg": msg})


EXCEPTIONS = (BadRequestException,)
