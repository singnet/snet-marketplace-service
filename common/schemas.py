from enum import Enum
from common.exceptions import CustomException


class OrderEnum(str, Enum):
    ascending = "asc"
    descending = "desc"


class PayloadValidationError(CustomException):
    def __init__(self):
        super().__init__(message="Error in parsing payload")
