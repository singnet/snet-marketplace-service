from common.exceptions import CustomException


class EventTypeNotFoundException(CustomException):
    error_message = "INVALID_EVENT_TYPE"

    def __init__(self):
        super().__init__({})
