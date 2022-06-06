from common.exceptions import MethodNotImplemented, OperationNotAllowed, CustomException

EXCEPTIONS = (MethodNotImplemented, OperationNotAllowed)


class InvalidFilePath(CustomException):

    def __init__(self, file_path=None):
        super().__init__(error_details=f"File not found in path {file_path}")

