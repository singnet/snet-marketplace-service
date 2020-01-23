class BadRequestException(Exception):
    pass


class OrganizationNotFound(Exception):
    pass


class CustomException(Exception):
    def __init__(self, error_details):
        self.ERROR_DETAILS = error_details
