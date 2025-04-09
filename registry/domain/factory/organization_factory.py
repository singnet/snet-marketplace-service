from registry.settings import settings
from registry.constants import Role, OrganizationAddressType
from registry.domain.models.comment import Comment
from registry.domain.models.group import Group
from registry.domain.models.organization import Organization, OrganizationState
from registry.domain.models.organization_address import OrganizationAddress
from registry.domain.models.organization_member import OrganizationMember
from registry.exceptions import InvalidOriginException, BadRequestException


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
        if origin not in settings.aws.ALLOWED_ORIGIN:
            raise InvalidOriginException()
        contacts = payload["contacts"]
        assets = payload["assets"]
        metadata_uri = payload["metadata_uri"]
        groups = OrganizationFactory.group_domain_entity_from_group_list_payload(payload["groups"])
        addresses = OrganizationFactory \
            .domain_address_entity_from_address_list_payload(payload["org_address"]["addresses"])
        organization = Organization(
            org_uuid, org_id, org_name, org_type, origin, description, short_description, url, contacts,
            assets, metadata_uri, duns_no, groups, addresses, None, [])
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
        if address_type not in [OrganizationAddressType.HEAD_QUARTER_ADDRESS.value,
                                OrganizationAddressType.MAIL_ADDRESS.value]:
            raise BadRequestException()
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
    def get_comment_from_db(comments):
        return [Comment(comment['comment'], comment['created_by'], comment['created_at']) for comment in comments]

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
            metadata_uri=organization_repo_model.metadata_uri,
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
        return OrganizationState(
            org_uuid=item.org_uuid,
            state=item.state, transaction_hash=item.transaction_hash, wallet_address=item.wallet_address,
            created_on=item.created_on, updated_on=item.updated_on, updated_by=item.updated_by,
            reviewed_by=item.reviewed_by, reviewed_on=item.reviewed_on,
            comments=OrganizationFactory.get_comment_from_db(item.comments), created_by=item.created_by)

    @staticmethod
    def parse_organization_state_from_db(item):
        return OrganizationState(
            org_uuid=item.org_uuid, state=item.state, transaction_hash=item.transaction_hash,
            wallet_address=item.wallet_address,
            created_on=item.created_on, updated_on=item.updated_on, updated_by=item.updated_by,
            reviewed_by=item.reviewed_by, reviewed_on=item.reviewed_on,
            comments=OrganizationFactory.get_comment_from_db(item.comments),
            created_by=item.created_by)

    @staticmethod
    def parse_organization_state_from_db_list(org_state_db_list):
        return [OrganizationFactory.parse_organization_state_from_db(org_state) for org_state in org_state_db_list]

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

    @staticmethod
    def parse_group_domain_entity_from_metadata(payload):
        group_id = payload["group_id"]
        group_name = payload["group_name"]
        payment_address = payload['payment']["payment_address"]
        payment_config = {"payment_expiration_threshold": payload['payment']["payment_expiration_threshold"],
                          "payment_channel_storage_type": payload['payment']["payment_channel_storage_type"],
                          "payment_channel_storage_client": payload['payment']["payment_channel_storage_client"]}
        group = Group(group_name, group_id, payment_address, payment_config, '')
        group.setup_id()
        return group

    @staticmethod
    def group_domain_entity_from_group_list_metadata(payload):
        domain_group_entity = []
        for group in payload:
            domain_group_entity.append(OrganizationFactory.parse_group_domain_entity_from_metadata(group))
        return domain_group_entity

    @staticmethod
    def parser_org_members_from_metadata(org_uuid, members, status):

        org_members = []
        for member in members:
            org_members.append(OrganizationMember(org_uuid, "", status, Role.MEMBER.value, member))
        return org_members

    @staticmethod
    def parser_org_owner_from_metadata(org_uuid, owner, status):
        return OrganizationMember(org_uuid, "", status, Role.OWNER.value, owner)

    @staticmethod
    def parse_organization_metadata_assets(assets, existing_assets):
        url = ""
        for key, value in assets.items():
            if existing_assets and key in existing_assets:
                if existing_assets[key] and 'url' in existing_assets[key]:
                    url = existing_assets[key]['url']
            else:
                url = ""

            assets[key] = {
                "hash": value,
                "url": url
            }
        merged = {**existing_assets, **assets}
        return merged

    # @staticmethod
    # def parse_organization_metadata(org_uuid, ipfs_org_metadata, origin, duns_no, addresses, metadata_uri,
    #                                 existing_assets, transaction_hash, members):
    #     org_id = ipfs_org_metadata.get("org_id", None)
    #     org_name = ipfs_org_metadata.get("org_name", None)
    #     org_type = ipfs_org_metadata.get("org_type", None)
    #     description = ipfs_org_metadata.get("description", None)
    #     short_description = ""
    #     url = ""
    #     long_description = ""
    #
    #     if description:
    #         short_description = description.get("short_description", None)
    #         long_description = description.get("description", None)
    #         url = description.get("url", None)
    #
    #     contacts = ipfs_org_metadata.get("contacts", None)
    #     assets = OrganizationFactory.parse_organization_metadata_assets(ipfs_org_metadata.get("assets", {}),
    #                                                                     existing_assets)
    #     metadata_ipfs_hash = metadata_uri
    #     owner = ""
    #     groups = OrganizationFactory.group_domain_entity_from_group_list_metadata(ipfs_org_metadata.get("groups", []))
    #
    #     organization = Organization(org_uuid, org_id, org_name, org_type,
    #                                 origin, long_description,
    #                                 short_description, url, contacts, assets, metadata_ipfs_hash,
    #                                 duns_no, groups,
    #                                 addresses,
    #                                 OrganizationStatus.PUBLISHED.value,
    #                                 members)
    #     return organization
