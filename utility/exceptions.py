from common.exceptions import CustomException


class BadRequestException(CustomException):
    error_message = "BAD_REQUEST"

    def __init__(self):
        super().__init__({})


class InvalidContentType(CustomException):
    error_message = "INVALID_CONTENT_TYPE"

    def __init__(self):
        super().__init__({})

class ProtoNotFound(CustomException):
    error_message = "PROTO_NOT_FOUND"

    def __init__(self):
        super().__init__({})

class InvalidUploadType(CustomException):
    error_message = "INVALID_UPLOAD_TYPE"

    def __init__(self):
        super().__init__({})

class EmptyFileException(CustomException):
    error_message = "EMPTY_FILE"

    def __init__(self):
        super().__init__({})

class MissingUploadTypeDetailsParams(CustomException):
    error_message = "MISSING_UPLOAD_TYPE_DETAILS_PARAMS"

    def __init__(self):
        super().__init__({})


EXCEPTIONS = (BadRequestException, InvalidContentType)
