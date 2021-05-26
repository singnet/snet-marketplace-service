from common.exceptions import MethodNotImplemented, OperationNotAllowed, CustomException

EXCEPTIONS = (MethodNotImplemented, OperationNotAllowed)


class TimedOutException(CustomException):
    error_message = "PROCESS_TIMED_OUT"

    def __init__(self):
        super().__init__({})
