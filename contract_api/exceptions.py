from common.exceptions import MethodNotImplemented, OperationNotAllowed, CustomException

EXCEPTIONS = (MethodNotImplemented, OperationNotAllowed)


class InvalidFilePath(CustomException):

    def __init__(self, file_path=None):
        super().__init__(error_details=f"File not found in path {file_path}")

class LighthouseInternalException(CustomException):
    error_message = "LIGHTHOUSE_INTERNAL_SERVER_ERROR"

    def __init__(self):
        super().__init__({})