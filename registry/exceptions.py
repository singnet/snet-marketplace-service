class CustomException(Exception):
    def __init__(self, response, error_details):
        self.RESPONSE = response
        self.ERROR_DETAILS = error_details


class OrganizationNotFoundException(CustomException):
    ERROR_MESSAGE = "ORG_NOT_FOUND"
    ERROR_CODE = 0

    def __init__(self, response, org_uuid):
        error_details = {
            "org_uuid": org_uuid
        }
        super().__init__(response, error_details)


class MemberAlreadyExists(CustomException):
    ERROR_MESSAGE = "MEMBER_ALREADY_EXISTS"
    ERROR_CODE = 0

    def __init__(self, response, org_uuid, failed_member_list):
        error_details = {
            "org_uuid": org_uuid,
            "failed_to_invite_members": failed_member_list
        }
        super().__init__(response, error_details)


EXCEPTIONS = (OrganizationNotFoundException, MemberAlreadyExists)
