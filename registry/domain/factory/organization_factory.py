from registry.config import ALLOWED_ORIGIN
from registry.domain.models.group import Group
from registry.domain.models.organization import Organization, OrganizationState
from registry.domain.models.organization_address import OrganizationAddress
from registry.domain.models.organization_member import OrganizationMember
from registry.exceptions import InvalidOrigin


class OrganizationFactory:

    @staticmethod
    def org_domain_entity_from_payload(payload):

        org_uuid = payload["org_uuid"]
        org_id = payload["org_id"]
        org_name = payload["org_name"]
        org_type = payload["org_type"]
        description = payload["description"]
        short_description = payload["short_description"]
        url = payload["url"]
        duns_no = payload["duns_no"]
        origin = payload["origin"]
        if origin not in ALLOWED_ORIGIN:
            raise InvalidOrigin()
        contacts = payload["contacts"]
        assets = payload["assets"]
        metadata_ipfs_uri = payload["metadata_ipfs_uri"]
        groups = OrganizationFactory.group_domain_entity_from_group_list_payload(payload["groups"])
        addresses = OrganizationFactory\
            .domain_address_entity_from_address_list_payload(payload["org_address"]["addresses"])
        organization = Organization(
            org_uuid, org_id, org_name, org_type, origin, description, short_description, url, contacts,
            assets, metadata_ipfs_uri, duns_no, groups, addresses, None, [])
        return organization

    @staticmethod
    def group_domain_entity_from_payload(payload):
        group_id = payload["id"]
        group_name = payload["name"]
        payment_address = payload["payment_address"]
        payment_config = payload["payment_config"]
        group = Group(group_name, group_id, payment_address, payment_config, '')
        group.setup_id()
        return group

    @staticmethod
    def group_domain_entity_from_group_list_payload(payload):
        domain_group_entity = []
        for group in payload:
            domain_group_entity.append(OrganizationFactory.group_domain_entity_from_payload(group))
        return domain_group_entity

    @staticmethod
    def domain_address_entity_from_payload(payload):
        address_type = payload.get("address_type", None)
        street_address = payload.get("street_address", None)
        apartment = payload.get("apartment", None)
        city = payload.get("city", None)
        pincode = payload.get("pincode", None)
        state = payload.get("state", None)
        country = payload.get("country", None)
        address = OrganizationAddress(address_type=address_type, street_address=street_address, apartment=apartment,
                                      pincode=pincode, city=city, state=state, country=country)
        return address

    @staticmethod
    def domain_address_entity_from_address_list_payload(raw_addresses):
        addresses = []
        for address in raw_addresses:
            addresses.append(OrganizationFactory.domain_address_entity_from_payload(address))
        return addresses

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
            metadata_ipfs_uri=organization_repo_model.metadata_ipfs_uri,
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
                                 reviewed_by=item.reviewed_by, reviewed_on=item.reviewed_on, created_by=item.created_by)

    @staticmethod
    def org_domain_entity_from_repo_model_list(organization_repo_model_list):
        organization_domain_entity = []
        for organization_repo_model in organization_repo_model_list:
            organization_domain_entity.append(
                OrganizationFactory.org_domain_entity_from_repo_model(organization_repo_model))
        return organization_domain_entity

    @staticmethod
    def org_member_domain_from_repo_model_list(org_member_repo_model_list):
        org_member_domain_entity = []
        for org_member_repo_model in org_member_repo_model_list:
            org_member_domain_entity.append(
                OrganizationFactory.org_member_domain_entity_from_repo_model(org_member_repo_model))
        return org_member_domain_entity

    @staticmethod
    def org_member_domain_entity_from_repo_model(org_member_repo_model):
        org_member = OrganizationMember(
            org_member_repo_model.org_uuid, org_member_repo_model.username, org_member_repo_model.status,
            org_member_repo_model.role, org_member_repo_model.address, org_member_repo_model.invite_code,
            org_member_repo_model.transaction_hash, org_member_repo_model.invited_on, org_member_repo_model.updated_on)
        return org_member

    @staticmethod
    def org_member_domain_entity_from_payload_list(payload, org_uuid):
        org_member_list = []
        for org_member in payload:
            org_member_list.append(OrganizationFactory.org_member_domain_entity_from_payload(org_member, org_uuid))
        return org_member_list

    @staticmethod
    def org_member_domain_entity_from_payload(payload, org_uuid):
        username = payload.get("username", "")
        status = payload.get("status", "")
        role = payload.get("role", "")
        address = payload.get("address", "")
        invite_code = payload.get("invite_code", "")
        transaction_hash = payload.get("transaction_hash", "")
        org_member = OrganizationMember(org_uuid, username, status, role, address, invite_code, transaction_hash)
        return org_member
