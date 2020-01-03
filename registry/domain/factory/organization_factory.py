import base64

import common.boto_utils as boto_utils

from datetime import datetime
from common.logger import get_logger
from registry.config import METADATA_FILE_PATH, ASSET_BUCKET, REGION_NAME
from registry.domain.models.group import Group
from registry.domain.models.organization import Organization
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
                current_time = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                key_name = f"{uuid}-{asset_type}-{current_time}.{asset['file_type']}"
                filename = f"{METADATA_FILE_PATH}/{key_name}"
                raw_file = base64.b64decode(asset["raw"].encode())
                with open(filename, 'wb') as image:
                    image.write(raw_file)
                boto_client.s3_upload_file(filename, ASSET_BUCKET, key_name)
                asset_url = f"https://{ASSET_BUCKET}.s3.amazonaws.com/{key_name}"
                org_assets[asset_type]["url"] = asset_url
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
        contacts = payload.get("contacts", None)
        metadata_ipfs_hash = payload.get("metadata_ipfs_hash", None)
        groups = OrganizationFactory.parse_raw_list_groups(payload.get("groups", []))
        addresses = OrganizationFactory.parse_raw_address_list(payload.get("addresses", []))
        organization = Organization(name=org_name, org_id=org_id, org_uuid=org_uuid, org_type=org_type,
                                    description=description, short_description=short_description, url=url,
                                    contacts=contacts, assets=assets, metadata_ipfs_hash=metadata_ipfs_hash,
                                    duns_no=duns_no, groups=groups, addresses=addresses)
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
    def parse_organization_data_model(item):
        organization = Organization(
            item.name, item.org_id, item.org_uuid, item.type, item.description,
            item.short_description, item.url, item.contacts, item.assets, item.metadata_ipfs_hash,
            item.duns_no, OrganizationFactory.parse_organization_address_data_model(item.address),
            OrganizationFactory.parse_group_data_model(item.groups)
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
            organizations.append(OrganizationFactory.parse_organization_data_model(item.Organization))
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
