from enum import Enum

from registry.infrastructure.repositories.organization_repository import OrganizationRepository


class Role(Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class Action(Enum):
    CREATE = "CREATE"
    SUBMIT = "SUBMIT"
    PUBLISH = "PUBLISH"
    UPDATE = "UPDATE"
    READ = "READ"


POLICY = {Role.OWNER: [Action.CREATE, Action.SUBMIT, Action.PUBLISH, Action.UPDATE, Action.READ],
          Role.MEMBER: [Action.CREATE, Action.SUBMIT, Action.UPDATE, Action.READ]}

org_repo = OrganizationRepository()


def is_access_allowed(username, action, org_uuid):
    org_member_details = org_repo.get_member_details_for_org(username, org_uuid)

    if not org_member_details:
        return False
    role = org_member_details.role

    if action in POLICY[role]:
        return True
    return False


def secured(*decorator_args, **decorator_kwargs):
    action = decorator_kwargs["action"]

    def check_access(func):
        def wrapper(self, *args, **kwargs):
            if is_access_allowed(self.username, action, self.org_uuid):
                return func(self, *args, **kwargs)
            raise Exception("Operation Not allowed")

        return wrapper

    return check_access
