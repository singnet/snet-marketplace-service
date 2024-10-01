import json
from collections import defaultdict
from typing import Any, Optional, List, Dict

from sqlalchemy.sql import func

from contract_api.infrastructure.repositories.base_repository import BaseRepository
from contract_api.infrastructure.models import Organization, Service, Members, OrgGroup
from contract_api.domain.factory.organization_factory import OrganizationFactory
from contract_api.domain.models.organization import (OrganizationEntityModel,
                                                     OrganizationGroupEntityModel)
from common.logger import get_logger 

logger = get_logger(__name__)

class OrganizationRepository(BaseRepository):

    def get_organization(self, org_id: str=None, org_name: str=None) -> Optional[OrganizationEntityModel]:
        query = self.session.query(Organization)

        if org_id is not None:
            query = query.filter_by(org_id = org_id)

        if org_name is not None:
            query = query.filter_by(org_name = org_name)

        organization = query.first()
        return OrganizationFactory.convert_to_organization_entity_model_from_db_model(organization) \
            if organization else None

    def get_organizations(self) -> List[OrganizationEntityModel]:
        oraganizations = self.session.query(Organization).all()
        return [
            OrganizationFactory.convert_to_organization_entity_model_from_db_model(organization)
                for organization in oraganizations
        ]

    def get_organization_details(self, org_id: str):
        session = self.session
        org_details = (
            session.query(Organization, func.count(Service.id).label('service_count'))
            .join(Service, Service.org_id == Organization.org_id)
            .filter(Organization.org_id == org_id)
            .group_by(Organization.org_id)
            .first()
        )

        if not org_details:
            return None

        organization, service_count = org_details
        return {
            "org_id": organization.org_id,
            "organization_name": organization.organization_name,
            "service_count": service_count
        }

    def get_all_members(self, org_id: Optional[str] = None) -> Dict[str, List[str]]:
        query = self.session.query(Members)

        if org_id is not None:
            query = query.filter(Members.org_id == org_id)

        all_orgs_members_raw = query.all()
        all_orgs_members = defaultdict(list)

        for rec in all_orgs_members_raw:
            all_orgs_members[rec[0]].append(rec[1])  # rec[0] = org_id, rec[1] = member

        return all_orgs_members

    def get_group_by_org_id(self, org_id: str) -> OrganizationGroupEntityModel:
        organization_group = self.session.query(OrgGroup). \
            filter_by(org_id=org_id).first()
        return OrganizationFactory.convert_to_organization_group_enity_model_from_db_model(
            organization_group_db=organization_group
        )
    
    def get_group_details_for_org_id(self, org_id: int, group_id: int) -> Dict[str, Any]:
        """
        Method to get group data for a given org_id and group_id. This includes group data at the org level.
        """

        group_data = self.session.query(Organization).filter_by(org_id=org_id, group_id=group_id).all()

        groups = []
        for group_record in group_data:
            try:
                group_record_dict = {
                    "group_id": group_record.group_id,
                    "group_name": group_record.group_name,
                    "payment": json.loads(group_record.payment),
                    "org_id": group_record.org_id
                }
            except json.JSONDecodeError as e:
                logger.Error(f"Error decoding JSON for payment: {e}")
                group_record_dict["payment"] = None

            groups.append(group_record_dict)

        return {"groups": groups}
