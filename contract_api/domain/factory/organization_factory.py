from contract_api.infrastructure.models import Organization
from contract_api.domain.models.organization import OrganizationEntityModel


class OrganizationFactory:

    @staticmethod
    def convert_to_organization_entity_model_from_db_model(organization_db: Organization):
        return OrganizationEntityModel(
            org_id=organization_db.org_id,
            organization_name=organization_db.organization_name,
            owner_address=organization_db.owner_address,
            org_metadata_uri=organization_db.org_metadata,
            org_email=organization_db.org_email,
            org_assets_url=organization_db.org_assets_url,
            is_currated=organization_db.is_curated,
            description=organization_db.is_curated,
            assets_hash=organization_db.assets_hash,
            contacts=organization_db.contacts
        )