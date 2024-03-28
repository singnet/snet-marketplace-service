from functools import reduce

from common.logger import get_logger
from registry.exceptions import ForbiddenException
from registry.constants import Action, Role
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository

org_repository = OrganizationPublisherRepository()

logger = get_logger(__name__)


def is_access_allowed(username, action, org_uuid):
    org_member_details = org_repository.get_org_member(username, org_uuid)
    if len(org_member_details) == 0:
        return False
    role = org_member_details[0].role
    if action in POLICY[Role[role]]:
        return True
    return False


POLICY = {Role.OWNER: [Action.CREATE, Action.SUBMIT, Action.PUBLISH, Action.UPDATE, Action.READ],
          Role.MEMBER: [Action.CREATE, Action.SUBMIT, Action.UPDATE, Action.READ]}


def secured(*decorator_args, **decorator_kwargs):
    action = decorator_kwargs["action"]
    org_uuid_path = decorator_kwargs["org_uuid_path"]
    username_path = decorator_kwargs["username_path"]

    def check_access(func):
        def wrapper(*args, **kwargs):
            if 'event' in kwargs:
                org_uuid = reduce(dict.get, org_uuid_path, kwargs['event'])
                username = reduce(dict.get, username_path, kwargs['event'])
            else:
                event, context = args
                org_uuid = reduce(dict.get, org_uuid_path, event)
                username = reduce(dict.get, username_path, event)
            if is_access_allowed(username, action, org_uuid):
                return func(*args, **kwargs)
            raise ForbiddenException()

        return wrapper

    return check_access
