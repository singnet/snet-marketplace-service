from enum import Enum
from common.exceptions import BadRequestException


class OrderEnum(str, Enum):
    ascending = "asc"
    descending = "desc"


class PayloadValidationError(BadRequestException):
    def __init__(self):
        super().__init__("Error in parsing payload")
