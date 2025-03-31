class BadRequestException(Exception):
    pass


class OrganizationNotFound(Exception):
    pass


class CustomException(Exception):

    def __init__(self, error_details):
        self.error_details = error_details
        if "msg" in error_details:
            super().__init__(error_details["msg"])


class MethodNotImplemented(CustomException):
    error_message = "METHOD_NOT_IMPLEMENTED"

    def __init__(self):
        super().__init__({})


class OperationNotAllowed(CustomException):
    error_message = "OPERATION_NOT_ALLOWED"

    def __init__(self):
        super().__init__({})
