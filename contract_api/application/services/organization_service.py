from contract_api.application.schemas.organization_schemas import GetGroupRequest
from contract_api.infrastructure.repositories.organization_repository import OrganizationRepository


class OrganizationService:
    def __init__(self):
        self._org_repo = OrganizationRepository()

    # is used in handler
    def get_all_organizations(self) -> list[dict]:
        orgs = self._org_repo.get_organizations_with_curated_services()
        org_data = [org.to_response() for org in orgs]

        return org_data

    # is used in handler
    def get_group(self, request: GetGroupRequest) -> dict:
        org_id = request.org_id
        group_id = request.group_id

        groups = self._org_repo.get_groups(org_id, group_id)
        group_data = [group.to_response() for group in groups]

        return {"groups": group_data}
