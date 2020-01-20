import base64
from datetime import datetime

import common.boto_utils as boto_utils
from common.logger import get_logger
from registry.config import ALLOWED_ORIGIN, ASSET_BUCKET, METADATA_FILE_PATH, REGION_NAME
from registry.constants import OrganizationMemberStatus, OrganizationStatus, Role
from registry.domain.models.group import Group
from registry.domain.models.organization import Organization, OrganizationMember
from registry.domain.models.organization_address import OrganizationAddress

logger = get_logger(__name__)


class OrganizationFactory:

    @staticmethod
    def parse_raw_organization(payload):

        def extract_and_upload_assets(uuid, raw_assets):
            org_assets = {}
            boto_client = boto_utils.BotoUtils(region_name=REGION_NAME)
            for asset_type in raw_assets:
                org_assets[asset_type] = {}
                asset = raw_assets[asset_type]
                if "raw" in asset and len(asset["raw"]) != 0:
                    current_time = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                    key_name = f"{uuid}-{asset_type}-{current_time}.{asset['file_type']}"
                    filename = f"{METADATA_FILE_PATH}/{key_name}"
                    raw_file = base64.b64decode(asset["raw"].encode())
                    with open(filename, 'wb') as image:
                        image.write(raw_file)
                    boto_client.s3_upload_file(filename, ASSET_BUCKET, key_name)
                    asset_url = f"https://{ASSET_BUCKET}.s3.amazonaws.com/{key_name}"
                    org_assets[asset_type]["url"] = asset_url
                if "url" in asset:
                    org_assets[asset_type]["url"] = asset["url"]
            return org_assets

        org_id = payload.get("org_id", None)
        org_name = payload.get("org_name", None)
        org_type = payload.get("org_type", None)
        org_uuid = payload.get("org_uuid", None)
        description = payload.get("description", None)
        assets = {}
        short_description = payload.get("short_description", None)
        url = payload.get("url", None)
        duns_no = payload.get("duns_no", None)
        origin = payload.get("origin", None)
        if origin not in ALLOWED_ORIGIN:
            raise Exception(f"Invalid origin {origin}")
        owner_name = payload.get("owner_name", None)
        contacts = payload.get("contacts", None)
        metadata_ipfs_hash = payload.get("metadata_ipfs_hash", None)
        groups = OrganizationFactory.parse_raw_list_groups(payload.get("groups", []))
        addresses = OrganizationFactory.parse_raw_address_list(payload.get("addresses", []))
        organization = Organization(
            name=org_name, org_id=org_id, org_uuid=org_uuid, org_type=org_type, description=description,
            short_description=short_description, url=url, contacts=contacts, assets=assets,
            metadata_ipfs_hash=metadata_ipfs_hash, duns_no=duns_no, owner_name=owner_name, groups=groups,
            addresses=addresses, owner="", status="", origin=origin)
        organization.setup_id()
        organization.assets = extract_and_upload_assets(organization.org_uuid, payload.get("assets", {}))
        return organization

    @staticmethod
    def parse_raw_list_groups(raw_groups):
        groups = []
        for group in raw_groups:
            groups.append(OrganizationFactory.parse_raw_group(group))
        return groups

    @staticmethod
    def parse_raw_address_list(raw_addresses):
        addresses = []
        for address in raw_addresses:
            addresses.append(OrganizationFactory.parse_raw_address(address))
        return addresses

    @staticmethod
    def parse_raw_group(raw_group):
        group_id = raw_group.get("id", None)
        group_name = raw_group.get("name", None)
        payment_address = raw_group.get("payment_address", None)
        payment_config = raw_group.get("payment_config", None)
        group = Group(group_name, group_id, payment_address, payment_config, '')
        return group

    @staticmethod
    def parse_raw_address(raw_address):
        address_type = raw_address.get("address_type", None)
        street_address = raw_address.get("street_address", None)
        apartment = raw_address.get("apartment", None)
        city = raw_address.get("city", None)
        pincode = raw_address.get("pincode", None)
        state = raw_address.get("state", None)
        country = raw_address.get("country", None)
        address = OrganizationAddress(address_type=address_type, street_address=street_address, apartment=apartment,
                                      pincode=pincode, city=city, state=state, country=country)
        return address

    @staticmethod
    def org_member_from_dict(org_member, org_uuid):
        username = org_member.get("username", "")
        status = org_member.get("status", "")
        role = org_member.get("role", "")
        address = org_member.get("address", "")
        invite_code = org_member.get("invite_code", "")
        transaction_hash = org_member.get("transaction_hash", "")
        org_member = OrganizationMember(org_uuid, username, status, role, address, invite_code, transaction_hash)
        return org_member

    @staticmethod
    def org_member_from_dict_list(org_member_dict_list, org_uuid):
        org_member_list = []
        for org_member in org_member_dict_list:
            org_member_list.append(OrganizationFactory.org_member_from_dict(org_member, org_uuid))
        return org_member_list

    @staticmethod
    def parse_organization_data_model(item, status):
        organization = Organization(
            item.name, item.org_id, item.org_uuid, item.type, item.owner, item.description,
            item.short_description, item.url, item.contacts, item.assets, item.metadata_ipfs_hash,
            item.duns_no, item.origin, OrganizationFactory.parse_organization_address_data_model(item.address),
            OrganizationFactory.parse_group_data_model(item.groups), status, item.owner_name
        )
        return organization

    @staticmethod
    def parse_organization_data_model_list(items):
        organizations = []
        for item in items:
            organizations.append(OrganizationFactory.parse_organization_data_model(item))
        return organizations

    @staticmethod
    def parse_organization_workflow_data_model_list(items):
        organizations = []
        for item in items:
            organizations.append(
                OrganizationFactory.parse_organization_data_model(
                    item.Organization, item.OrganizationReviewWorkflow.status)
            )
        return organizations

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
    def parse_organization_details(items):
        orgs = []
        for item in items:
            orgs.append(OrganizationFactory.parse_organization_data_model(item.Organization,
                                                                          item.OrganizationReviewWorkflow.status))

        return orgs

    @staticmethod
    def parse_organization_metadata_assets(assets):
        if assets is None:
            return None
        for key, value in assets.items():
            assets[key] = {
                "ipfs_hash": value,
                "url": ""
            }
        return assets

    @staticmethod
    def parse_organization_metadata(ipfs_org_metadata):
        org_id = ipfs_org_metadata.get("org_id", None)
        org_name = ipfs_org_metadata.get("name", None)
        org_type = ipfs_org_metadata.get("org_type", None)
        description = ipfs_org_metadata.get("description", None)
        short_description = ""
        url = ""
        long_description = ""

        if description:
            short_description = description.get("short_description", None)
            long_description = description.get("description", None)
            url = description.get("url", None)

        contacts = ipfs_org_metadata.get("contacts", None)
        assets = OrganizationFactory.parse_organization_metadata_assets(ipfs_org_metadata.get("assets", None))
        metadata_ipfs_hash = ipfs_org_metadata.get("metadata_ipfs_hash", None)
        owner = ""
        groups = OrganizationFactory.parse_raw_list_groups(ipfs_org_metadata.get("groups", []))

        organization = Organization(org_name, org_id, "", org_type, owner, long_description,
                                    short_description, url, contacts, assets, metadata_ipfs_hash, "", "", [], groups,
                                    OrganizationStatus.PUBLISHED.value)

        return organization

    @staticmethod
    def org_member_list_from_db(org_member_items):
        members = []
        for member_item in org_member_items:
            members.append(OrganizationFactory.org_member_from_db(member_item))
        return members

    @staticmethod
    def org_member_from_db(org_member_item):

        username = org_member_item.username
        role = org_member_item.role
        org_uuid = org_member_item.org_uuid
        address = org_member_item.address
        status = org_member_item.status
        invite_code = org_member_item.invite_code
        transaction_hash = org_member_item.transaction_hash
        org_member = OrganizationMember(org_uuid, username, status, role, address, invite_code, transaction_hash)

        return org_member

    @staticmethod
    def parser_org_members_from_metadata(org_uuid,members):

        org_members = []
        for member in members:
            org_members.append(OrganizationMember(org_uuid, "", OrganizationMemberStatus.PUBLISHED.value, Role.MEMBER.value, member))

        return org_members
