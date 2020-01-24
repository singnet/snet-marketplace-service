from common.exceptions import CustomException


class OrganizationNotFoundException(CustomException):
    error_message = "ORG_NOT_FOUND"
    error_code = 0

    def __init__(self, org_uuid):
        error_details = {
            "org_uuid": org_uuid
        }
        super().__init__(error_details)


class MemberAlreadyExists(CustomException):
    error_message = "MEMBER_ALREADY_EXISTS"
    error_code = 0

    def __init__(self, org_uuid, failed_member_list):
        error_details = {
            "org_uuid": org_uuid,
            "failed_to_invite_members": failed_member_list
        }
        super().__init__(error_details)


EXCEPTIONS = (OrganizationNotFoundException, MemberAlreadyExists)
