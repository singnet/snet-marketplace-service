import common.ipfs_util as ipfs_util
import requests

from urllib.parse import urlparse
from uuid import uuid4
from common.utils import json_to_file
from registry.config import IPFS_URL, METADATA_FILE_PATH, ASSET_DIR
from common.logger import get_logger

logger = get_logger(__name__)


class Organization:
    def __init__(self, name, org_id, org_uuid, org_type, description,
                 short_description, url, contacts, assets, metadata_ipfs_hash, duns_no, addresses, groups):
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
        self.org_uuid = org_uuid
        self.org_type = org_type
        self.description = description
        self.short_description = short_description
        self.url = url
        self.__duns_no = duns_no
        self.contacts = contacts
        self.assets = assets
        self.metadata_ipfs_hash = metadata_ipfs_hash
        self.groups = groups
        self.__addresses = addresses

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
            "contacts": self.contacts,
            "assets": self.assets,
            "metadata_ipfs_hash": self.metadata_ipfs_hash,
            "groups": [group.to_dict() for group in self.groups],
            "addresses": [address.to_dict() for address in self.addresses]
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
            url = self.assets[asset_type]["url"]
            filename = urlparse(url).path.split("/")[-1]
            response = requests.get(url)
            filepath = f"{ASSET_DIR}/{filename}"
            with open(filepath, 'wb') as asset_file:
                asset_file.write(response.content)
            asset_ipfs_hash = ipfs_utils.write_file_in_ipfs(filepath)
            self.assets[asset_type]["ipfs_hash"] = asset_ipfs_hash

    def publish_org(self):
        self.publish_assets()
        ipfs_utils = ipfs_util.IPFSUtil(IPFS_URL['url'], IPFS_URL['port'])
        metadata = self.to_metadata()
        filename = f"{METADATA_FILE_PATH}/{self.org_uuid}_org_metadata.json"
        json_to_file(metadata, filename)
        self.metadata_ipfs_hash = ipfs_utils.write_file_in_ipfs(filename)

    @property
    def duns_no(self):
        return self.__duns_no

    @property
    def addresses(self):
        return self.__addresses
