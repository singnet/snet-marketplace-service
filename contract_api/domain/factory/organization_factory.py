from typing import Sequence

from contract_api.domain.models.org_group import OrgGroupDomain
from contract_api.domain.models.organization import OrganizationDomain
from contract_api.infrastructure.models import OrgGroup, Organization


class OrganizationFactory:

    @staticmethod
    def org_groups_from_db_model(
            org_group_db_model_list: Sequence[OrgGroup]
    ) -> list[OrgGroupDomain]:
        result = []
        for org_group_db_model in org_group_db_model_list:
            result.append(OrgGroupDomain(
                row_id = org_group_db_model.row_id,
                org_id = org_group_db_model.org_id,
                group_id = org_group_db_model.group_id,
                group_name = org_group_db_model.group_name,
                payment = org_group_db_model.payment,
                created_on = org_group_db_model.created_on,
                updated_on = org_group_db_model.updated_on
            ))
        return result

    @staticmethod
    def orgs_from_db_model(
            orgs_db_model_list: Sequence[Organization]
    ) -> list[OrganizationDomain]:
        result = []
        for org_db_model in orgs_db_model_list:
            result.append(OrganizationDomain(
                row_id = org_db_model.row_id,
                org_id = org_db_model.org_id,
                organization_name = org_db_model.organization_name,
                owner_address = org_db_model.owner_address,
                org_metadata_uri = org_db_model.org_metadata_uri,
                org_email = org_db_model.org_email,
                org_assets_url = org_db_model.org_assets_url,
                is_curated = org_db_model.is_curated,
                description = org_db_model.description,
                assets_hash = org_db_model.assets_hash,
                contacts = org_db_model.contacts,
                created_on = org_db_model.created_on,
                updated_on = org_db_model.updated_on
            ))
        return result