from common.logger import get_logger

logger = get_logger(__name__)


class Organization:
    def __init__(self, name, org_id, org_type, description, short_description, url, contacts, assets, ipfs_hash):
        self.name = name
        self.org_id = org_id
        self.org_type = org_type
        self.description = description
        self.short_description = short_description
        self.url = url
        self.contacts = contacts
        self.assets = assets
        self.ipfs_hash = ipfs_hash
        self.groups = []

    def add_group(self, group):
        self.groups.append(group)

    def add_all_groups(self, groups):
        self.groups.extend(groups)

    def to_dict(self):
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
            "assets": {

            },
            "groups": [group.to_dict() for group in self.groups]
        }

    def validate_draft(self):
        validation = True
        validation_keys = [self.org_id, self.name, self.org_type]
        for key in validation_keys:
            if key is None or len(key):
                validation = False

        if self.short_description is not None and len(self.short_description) > 180:
            return False
        return validation

    def validate_approval_state(self):
        validation = False
        return self.validate_draft() and validation

    def validate_publish(self):
        return self.validate_approval_state() and (self.ipfs_hash is not None and len(self.ipfs_hash)!=0)