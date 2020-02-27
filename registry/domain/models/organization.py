from enum import Enum
from urllib.parse import urlparse
from uuid import uuid4

import requests

from common import ipfs_util
from common.utils import json_to_file, datetime_to_string
from registry.config import IPFS_URL, ASSET_DIR, METADATA_FILE_PATH
from registry.constants import OrganizationAddressType


class OrganizationType(Enum):
    ORGANIZATION = "organization"
    INDIVIDUAL = "individual"


class Organization:
    def __init__(self, uuid, org_id, name, org_type, origin, description, short_description, url,
                 contacts, assets, metadata_ipfs_uri, duns_no, groups, addresses, org_state, members):
        self.__name = name
        self.__id = org_id
        self.__uuid = uuid
        self.__org_type = org_type
        self.__description = description
        self.__short_description = short_description
        self.__url = url
        self.__duns_no = duns_no
        self.__origin = origin
        self.__contacts = contacts
        self.__assets = assets
        self.__metadata_ipfs_uri = metadata_ipfs_uri
        self.__groups = groups
        self.__addresses = addresses
        self.__state = org_state
        self.__members = members

    def to_metadata(self):
        assets = {}
        for key in self.__assets:
            assets[key] = self.__assets[key]["ipfs_uri"]
        return {
            "org_name": self.__name,
            "org_id": self.__id,
            "org_type": self.__org_type,
            "description": {
                "description": self.__description,
                "short_description": self.__short_description,
                "url": self.__url
            },
            "contacts": self.__contacts,
            "assets": assets,
            "groups": [group.to_metadata() for group in self.__groups]
        }

    def to_response(self):
        head_quarter_address = None
        mail_address = None
        mail_address_same_hq_address = False
        for address in self.addresses:
            if address.address_type == OrganizationAddressType.MAIL_ADDRESS:
                mail_address = address
            if address.address_type == OrganizationAddressType.HEAD_QUARTER_ADDRESS:
                head_quarter_address = address
        if mail_address is not None and head_quarter_address is not None and mail_address == head_quarter_address:
            mail_address_same_hq_address = True
        org_dict = {
            "org_name": self.__name,
            "org_id": self.__id,
            "org_uuid": self.__uuid,
            "org_type": self.__org_type,
            "description": self.__description,
            "short_description": self.__short_description,
            "url": self.__url,
            "duns_no": self.__duns_no,
            "origin": self.__origin,
            "contacts": self.__contacts,
            "assets": self.__assets,
            "metadata_ipfs_uri": self.__metadata_ipfs_uri,
            "groups": [group.to_response() for group in self.__groups],
            "org_address": {
                "mail_address_same_hq_address": mail_address_same_hq_address,
                "addresses": [address.to_response() for address in self.__addresses]
            },
            "state": {}
        }
        if self.__state is not None and isinstance(self.__state, OrganizationState):
            org_dict["state"] = self.__state.to_response()
        return org_dict

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__id

    @property
    def uuid(self):
        return self.__uuid

    @property
    def org_type(self):
        return self.__org_type

    @property
    def description(self):
        return self.__description

    @property
    def short_description(self):
        return self.__short_description

    @property
    def url(self):
        return self.__url

    @property
    def duns_no(self):
        return self.__duns_no

    @property
    def origin(self):
        return self.__origin

    @property
    def contacts(self):
        return self.__contacts

    @property
    def addresses(self):
        return self.__addresses

    @property
    def assets(self):
        return self.__assets

    @property
    def metadata_ipfs_uri(self):
        return self.__metadata_ipfs_uri

    @property
    def groups(self):
        return self.__groups

    @property
    def members(self):
        return self.__members

    @property
    def org_state(self):
        return self.__state

    def set_assets(self, assets):
        self.__assets = assets

    def set_state(self, state):
        self.__state = state

    def get_status(self):
        return self.__state.state

    def publish_assets(self):
        ipfs_utils = ipfs_util.IPFSUtil(IPFS_URL['url'], IPFS_URL['port'])
        for asset_type in self.__assets:
            if "url" in self.__assets[asset_type]:
                url = self.__assets[asset_type]["url"]
                filename = urlparse(url).path.split("/")[-1]
                response = requests.get(url)
                filepath = f"{ASSET_DIR}/{filename}"
                with open(filepath, 'wb') as asset_file:
                    asset_file.write(response.content)
                asset_ipfs_hash = ipfs_utils.write_file_in_ipfs(filepath)
                self.__assets[asset_type]["ipfs_uri"] = f"ipfs://{asset_ipfs_hash}"

    def publish_to_ipfs(self):
        self.publish_assets()
        ipfs_utils = ipfs_util.IPFSUtil(IPFS_URL['url'], IPFS_URL['port'])
        metadata = self.to_metadata()
        filename = f"{METADATA_FILE_PATH}/{self.__uuid}_org_metadata.json"
        json_to_file(metadata, filename)
        ipfs_hash = ipfs_utils.write_file_in_ipfs(filename, wrap_with_directory=False)
        self.__metadata_ipfs_uri = f"ipfs://{ipfs_hash}"

    def setup_id(self):
        org_uuid = uuid4().hex
        self.__uuid = org_uuid
        if self.__org_type == OrganizationType.INDIVIDUAL.value:
            self.__id = org_uuid

    def is_org_id_set(self):
        return self.__id is None or len(self.__id) == 0

    def is_org_uuid_set(self):
        return self.__uuid is None or len(self.__uuid) == 0

    def is_valid_field(self, field):
        if field is not None and len(field) != 0:
            return True
        return False

    def is_valid(self):
        if not self.is_valid_field(self.__name):
            return False
        if not self.is_valid_field(self.__uuid):
            return False
        if not self.is_valid_field(self.__id):
            return False
        if not self.is_valid_field(self.__org_type):
            return False
        if len(self.__groups) == 0:
            return False
        return True

    def is_minor(self, updated_organization):
        return True


class OrganizationState:
    def __init__(self, state, transaction_hash, wallet_address, created_by,
                 created_on, updated_on, updated_by, reviewed_by, reviewed_on):
        self.__state = state
        self.__transaction_hash = transaction_hash
        self.__wallet_address = wallet_address
        self.__created_by = created_by
        self.__created_on = created_on
        self.__updated_on = updated_on
        self.__updated_by = updated_by
        self.__reviewed_by = reviewed_by
        self.__reviewed_on = reviewed_on

    def to_response(self):
        state_dict = {
            "state": self.__state,
            "updated_on": "",
            "updated_by": self.__updated_by,
            "reviewed_by": self.__reviewed_by,
            "reviewed_on": "",
        }

        if self.__updated_on is not None:
            state_dict["updated_on"] = datetime_to_string(self.__updated_on)
        if self.__reviewed_on is not None:
            state_dict["reviewed_on"] = datetime_to_string(self.__reviewed_on)

        return state_dict

    def to_dict(self):
        state_dict = {
            "state": self.__state,
            "transaction_hash": self.__transaction_hash,
            "wallet_address": self.__wallet_address,
            "created_by": self.__created_by,
            "created_on": "",
            "updated_on": "",
            "updated_by": self.__updated_by,
            "reviewed_by": self.__reviewed_by,
            "reviewed_on": "",
        }

        if self.__updated_on is not None:
            state_dict["updated_on"] = datetime_to_string(self.__updated_on)
        if self.__reviewed_on is not None:
            state_dict["reviewed_on"] = datetime_to_string(self.__reviewed_on)
        if self.__created_on is not None:
            state_dict["created_on"] = datetime_to_string(self.__created_on)

        return state_dict

    @property
    def state(self):
        return self.__state

    @property
    def transaction_hash(self):
        return self.__transaction_hash

    @property
    def wallet_address(self):
        return self.__wallet_address

    @property
    def created_by(self):
        return self.__created_by

    @property
    def created_on(self):
        return self.__created_on

    @property
    def updated_on(self):
        return self.__updated_on

    @property
    def updated_by(self):
        return self.__updated_by

    @property
    def reviewed_by(self):
        return self.__reviewed_by

    @property
    def reviewed_on(self):
        return self.__reviewed_on
