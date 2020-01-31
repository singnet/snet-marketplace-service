from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository

org_repo = OrganizationPublisherRepository()


class OrganizationPublisherService:
    def __init__(self, org_uuid, username):
        self.org_uuid = org_uuid
        self.username = username

    def get_all_org_for_user(self):
        organizations = org_repo.get_org_for_user(username=self.username)
        return [org.to_dict() for org in organizations]
