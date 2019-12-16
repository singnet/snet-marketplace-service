

class Organization:
    def __init__(self, name, org_id, org_type, description, short_description, url, contacts, assets):
        if name is None:
            self.name = ""
        else:
            self.name = name

        if org_id is None:
            self.org_id = ""
        else:
            self.org_id = org_id

        if org_type is None:
            self.org_type = ""
        else:
            self.org_type = org_type

        if description is None:
            self.description = ""
        else:
            self.description = description

        if short_description is None:
            self.short_description = ""
        else:
            self.short_description = short_description

        if url is None:
            self.url = ""
        else:
            self.url = url

        if contacts is None:
            self.contacts = []
        else:
            self.contacts = contacts

        if assets is None:
            self.assets = {}
        else:
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
