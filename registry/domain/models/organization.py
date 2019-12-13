

class Organization:
    def __init__(self, name, org_id, org_type, description, short_description, url, contacts, assets):
        self.name = name
        self.org_id = org_id
        self.org_type = org_type
        self.description = description
        self.short_description = short_description
        self.url = url
        self.contacts = contacts
        self.assets = assets
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
            "groups": [ group.to_dict() for group in self.groups ]
        }
