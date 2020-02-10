class BadRequestException(Exception):
    pass


class OrganizationNotFound(Exception):
    pass


class CustomException(Exception):

    def __init__(self, error_details):
        self.error_details = error_details
