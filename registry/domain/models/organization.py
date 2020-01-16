from urllib.parse import urlparse
from uuid import uuid4

import requests
from deepdiff import DeepDiff

import common.ipfs_util as ipfs_util
from common.logger import get_logger
from common.utils import json_to_file
from registry.config import ASSET_DIR, IPFS_URL, METADATA_FILE_PATH
from registry.domain.models.organization_address import OrganizationAddress

logger = get_logger(__name__)
EXCLUDE_PATHS = ["root.org_uuid", "root._Organization__duns_no", "root.owner", "root._Organization__owner_name",
                 "root.assets['hero_image']['url']", "root.metadata_ipfs_hash", "root.origin"]


class Organization:
    def __init__(self, name, org_id, org_uuid, org_type, owner, description, short_description, url, contacts, assets,
                 metadata_ipfs_hash, duns_no, origin, addresses, groups, status, owner_name=None):
        """
        assets = [
            {
                "type": "hero_image",
                "hash": "12sjdf4db",
                "url": "https://dummy.dummy
            }
        ]
        """
        self.name = name
        self.org_id = org_id
        self.__owner_name = owner_name
        self.org_uuid = org_uuid
        self.org_type = org_type
        self.owner = owner
        self.description = description
        self.short_description = short_description
        self.url = url
        self.__duns_no = duns_no
        self.__origin = origin
        self.contacts = contacts
        self.assets = assets
        self.metadata_ipfs_hash = metadata_ipfs_hash
        self.groups = groups
        self.__addresses = addresses
        self.__status = status
        self.__members = []

    def setup_id(self):
        if self.is_org_uuid_set():
            self.org_uuid = uuid4().hex
        if self.org_type == "individual" and self.is_org_id_set():
            self.org_id = self.org_uuid

    def is_org_id_set(self):
        return self.org_id is None or len(self.org_id) == 0

    def is_org_uuid_set(self):
        return self.org_uuid is None or len(self.org_uuid) == 0

    def add_group(self, group):
        self.groups.append(group)

    def add_all_groups(self, groups):
        self.groups.extend(groups)

    def add_owner(self, owner):
        if self.owner is None or len(self.owner) == 0:
            self.owner = owner

    def to_metadata(self):
        assets = {}
        for key in self.assets:
            assets[key] = self.assets[key]["ipfs_hash"]
        return {
            "name": self.name,
            "org_id": self.org_id,
            "org_type": self.org_type,
            "description": {
                "description": self.description,
                "short_description": self.short_description,
                "url": self.url
            },
            "contacts": self.contacts,
            "assets": assets,
            "groups": [group.to_metadata() for group in self.groups]
        }

    def to_dict(self):
        return {
            "name": self.name,
            "org_id": self.org_id,
            "org_uuid": self.org_uuid,
            "org_type": self.org_type,
            "description": self.description,
            "short_description": self.short_description,
            "url": self.url,
            "duns_no": self.duns_no,
            "owner": self.owner,
            "origin": self.origin,
            "owner_name": self.owner_name,
            "contacts": self.contacts,
            "assets": self.assets,
            "metadata_ipfs_hash": self.metadata_ipfs_hash,
            "groups": [group.to_dict() for group in self.groups],
            "addresses": [address.to_dict() for address in self.addresses],
            "status": self.status
        }

    def is_valid_draft(self):
        validation = True
        validation_keys = [self.org_id, self.name, self.org_type, self.org_uuid]
        for key in validation_keys:
            if key is None or len(key) == 0:
                validation = False

        if self.short_description is not None and len(self.short_description) > 180:
            return False
        return validation

    def validate_approval_state(self):
        validation = False
        return self.is_valid_draft() and validation

    def validate_publish(self):
        return self.validate_approval_state() and (
            self.metadata_ipfs_hash is not None and len(self.metadata_ipfs_hash) != 0)

    def publish_assets(self):
        ipfs_utils = ipfs_util.IPFSUtil(IPFS_URL['url'], IPFS_URL['port'])
        for asset_type in self.assets:
            if "url" in self.assets[asset_type]:
                url = self.assets[asset_type]["url"]
                filename = urlparse(url).path.split("/")[-1]
                response = requests.get(url)
                filepath = f"{ASSET_DIR}/{filename}"
                with open(filepath, 'wb') as asset_file:
                    asset_file.write(response.content)
                asset_ipfs_hash = ipfs_utils.write_file_in_ipfs(filepath)
                self.assets[asset_type]["ipfs_hash"] = asset_ipfs_hash

    def publish_to_ipfs(self):
        self.publish_assets()
        ipfs_utils = ipfs_util.IPFSUtil(IPFS_URL['url'], IPFS_URL['port'])
        metadata = self.to_metadata()
        filename = f"{METADATA_FILE_PATH}/{self.org_uuid}_org_metadata.json"
        json_to_file(metadata, filename)
        self.metadata_ipfs_hash = ipfs_utils.write_file_in_ipfs(filename, wrap_with_directory=False)

    def is_major_change(self, metdata_organziation):
        return False

    def is_same_organization_as_organization_from_metadata(self, metadata_organization):
        diff = DeepDiff(self, metadata_organization, exclude_types=[OrganizationAddress],
                        exclude_paths=EXCLUDE_PATHS)

        logger.info(f"DIff for metadata organization {diff}")
        if not diff:
            return True
        return False

    @property
    def duns_no(self):
        return self.__duns_no

    @property
    def owner_name(self):
        return self.__owner_name

    @property
    def addresses(self):
        return self.__addresses

    @property
    def origin(self):
        return self.__origin

    @property
    def status(self):
        return self.__status

    @property
    def members(self):
        return self.__members


class OrganizationMember(object):
    def __init__(self, org_uuid, username, status, role, address=None, invite_code=None, transaction_hash=None):
        self.__role = role
        self.__org_uuid = org_uuid
        self.__username = username
        self.__status = status
        self.__address = address
        self.__invite_code = invite_code
        self.__transaction_hash = transaction_hash

    @property
    def username(self):
        return self.__username

    @property
    def status(self):
        return self.__status

    @property
    def address(self):
        return self.__address

    @property
    def role(self):
        return self.__role

    @property
    def invite_code(self):
        return self.__invite_code

    @property
    def transaction_hash(self):
        return self.__transaction_hash

    def set_transaction_hash(self, transaction_hash):
        self.__transaction_hash = transaction_hash

    def __repr__(self):
        return "Item(%s, %s,%s)" % (self.address, self.username, self.role)

    def __eq__(self, other):
        if isinstance(other, OrganizationMember):
            return self.address == other.address and self.username == other.username and self.role == other.role
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__repr__())

    def role_response(self):
        return {
            "username": self.username,
            "address": self.address,
            "role": self.role
        }

    def to_dict(self):
        return {
            "username": self.username,
            "address": self.address,
            "status": self.status,
            "role": self.role
        }

    def generate_invite_code(self):
        self.__invite_code = uuid4().hex
