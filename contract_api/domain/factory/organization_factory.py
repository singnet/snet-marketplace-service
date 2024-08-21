from contract_api.infrastructure.models import Organization, OrgGroup
from contract_api.domain.models.organization import OrganizationEntityModel, OrganizationGroupEntityModel


class OrganizationFactory:

    @staticmethod
    def convert_to_organization_entity_model_from_db_model(organization_db: Organization):
        return OrganizationEntityModel(
            org_id=organization_db.org_id,
            organization_name=organization_db.organization_name,
            owner_address=organization_db.owner_address,
            org_metadata_uri=organization_db.org_metadata_uri,
            org_email=organization_db.org_email,
            org_assets_url=organization_db.org_assets_url,
            is_currated=organization_db.is_curated,
            description=organization_db.is_curated,
            assets_hash=organization_db.assets_hash,
            contacts=organization_db.contacts
        )

    @staticmethod
    def convert_to_organization_group_enity_model_from_db_model(organization_group_db: OrgGroup):
        return OrganizationGroupEntityModel(
            org_id=organization_group_db.org_id,
            group_id=organization_group_db.group_id,
            group_name=organization_group_db.group_name,
            payment=organization_group_db.payment
        )