from registry.domain.models.group import Group
from registry.domain.models.organization import Organization, OrganizationState
from registry.domain.models.organization_address import OrganizationAddress


class OrganizationFactory:

    @staticmethod
    def org_domain_entity_from_repo_model(organization_repo_model):
        return Organization(
            uuid=organization_repo_model.uuid,
            name=organization_repo_model.name,
            org_id=organization_repo_model.org_id,
            org_type=organization_repo_model.org_type,
            origin=organization_repo_model.origin,
            description=organization_repo_model.description,
            short_description=organization_repo_model.short_description,
            url=organization_repo_model.url,
            contacts=organization_repo_model.contacts,
            assets=organization_repo_model.assets,
            metadata_ipfs_hash=organization_repo_model.metadata_ipfs_hash,
            duns_no=organization_repo_model.duns_no,
            groups=OrganizationFactory.parse_group_data_model(organization_repo_model.groups),
            addresses=OrganizationFactory.parse_organization_address_data_model(organization_repo_model.addresses),
            org_state=OrganizationFactory.parse_organization_state_data_model(organization_repo_model.org_state),
            members=[]
        )

    @staticmethod
    def parse_group_data_model(items):
        groups = []
        for group in items:
            groups.append(Group(group.name, group.id, group.payment_address, group.payment_config, group.status))
        return groups

    @staticmethod
    def parse_organization_address_data_model(items):
        addresses = []
        for address in items:
            addresses.append(
                OrganizationAddress(
                    address_type=address.address_type,
                    street_address=address.street_address,
                    apartment=address.apartment,
                    pincode=address.pincode,
                    city=address.city,
                    state=address.state,
                    country=address.country
                ))
        return addresses

    @staticmethod
    def parse_organization_state_data_model(item):
        if len(item) == 0:
            return []
        item = item[0]
        return OrganizationState(state=item.state, transaction_hash=item.transaction_hash, wallet_address="0x123",
                                 created_on=item.created_on, updated_on=item.updated_on, updated_by=item.updated_by,
                                 reviewed_by=item.reviewed_by, reviewed_on=item.reviewed_on)

    @staticmethod
    def org_domain_entity_from_repo_model_list(organization_repo_model_list):
        organization_domain_entity = []
        for organization_repo_model in organization_repo_model_list:
            organization_domain_entity.append(
                OrganizationFactory.org_domain_entity_from_repo_model(organization_repo_model))
        return organization_domain_entity
