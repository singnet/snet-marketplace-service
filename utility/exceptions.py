from common.exceptions import BadRequestException


class InvalidContentType(BadRequestException):
    def __init__(self):
        super().__init__(message="Invalid content type")

class ProtoNotFound(BadRequestException):
    def __init__(self):
        super().__init__(message="Proto file not nound")


EXCEPTIONS = (BadRequestException, InvalidContentType)
