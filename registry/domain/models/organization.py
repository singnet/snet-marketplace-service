from uuid import uuid4
from common.logger import get_logger

logger = get_logger(__name__)


class Organization:
    def __init__(self, name, org_id, org_uuid, org_type, description,
                 short_description, url, contacts, assets, metadata_ipfs_hash):
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
        self.contacts = contacts
        self.assets = assets
        self.metadata_ipfs_hash = metadata_ipfs_hash
        self.groups = []

    def set_metadata_ipfs_hash(self, metadata_ipfs_hash):
        self.metadata_ipfs_hash = metadata_ipfs_hash

    def setup_id(self):
        if self.org_uuid is None or len(self.org_uuid) == 0:
            self.org_uuid = uuid4().hex
        if self.org_type is "individual" and self.org_id is None:
            self.org_id = self.org_uuid

    def add_group(self, group):
        self.groups.append(group)

    def add_all_groups(self, groups):
        self.groups.extend(groups)

    def to_metadata(self):
        assets = {}
        for asset in self.assets:
            assets[asset["type"]] = asset["hash"]
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
            "contacts": self.contacts,
            "assets": self.assets,
            "metadata_ipfs_hash": self.metadata_ipfs_hash,
            "groups": [group.to_dict() for group in self.groups]
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
