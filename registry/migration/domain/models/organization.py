class Organization:
    def __init__(self, uuid, org_id, name, org_type, origin, description, short_description, url,
                 contacts, assets, metadata_uri, duns_no, members, groups):
        self.name = name
        self.id = org_id
        self.uuid = uuid
        self.org_type = org_type
        self.description = description
        self.short_description = short_description
        self.url = url
        self.duns_no = duns_no
        self.origin = origin
        self.contacts = contacts
        self.assets = assets
        self.metadata_uri = metadata_uri
        self.members = members
        self.groups = groups


class OrganizationMember:
    def __init__(self, org_uuid, username, status, role, address=None,
                 invite_code=None, transaction_hash=None, invited_on=None, updated_on=None, created_on=None):
        self.role = role
        self.org_uuid = org_uuid
        self.username = username
        self.status = status
        self.address = address
        self.invite_code = invite_code
        self.transaction_hash = transaction_hash
        self.created_on = created_on
        self.invited_on = invited_on
        self.updated_on = updated_on


class Group:
    def __init__(self, name, org_uuid, org_id, group_id, payment_address,
                 payment_config, status, created_at, updated_at):
        self.name = name
        self.org_id = org_id
        self.org_uuid = org_uuid
        self.group_id = group_id
        self.payment_address = payment_address
        self.payment_config = payment_config
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at