

class Organization:
    def __init__(self, uuid, org_id, name, org_type, origin, description, short_description, url,
                 contacts, assets, metadata_ipfs_hash, duns_no, groups, addresses, org_state, members):
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
        self.__metadata_ipfs_hash = metadata_ipfs_hash
        self.__groups = groups
        self.__addresses = addresses
        self.__state = org_state
        self.__members = members

    def to_metadata(self):
        assets = {}
        for key in self.__assets:
            assets[key] = self.__assets[key]["ipfs_hash"]
        return {
            "name": self.__name,
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

    def to_dict(self):
        org_dict = {
            "name": self.__name,
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
            "metadata_ipfs_hash": self.__metadata_ipfs_hash,
            "groups": [group.to_dict() for group in self.__groups],
            "addresses": [address.to_dict() for address in self.__addresses],
            "state": {}
        }
        if self.__state is not None and isinstance(self.__state, OrganizationState):
            org_dict["state"] = self.__state.to_dict()
        return org_dict

    @property
    def duns_no(self):
        return self.__duns_no

    @property
    def addresses(self):
        return self.__addresses

    @property
    def origin(self):
        return self.__origin

    @property
    def members(self):
        return self.__members


class OrganizationState:
    def __init__(self, state, transaction_hash, wallet_address,
                 created_on, updated_on, updated_by, reviewed_by, reviewed_on):
        self.__state = state
        self.__transaction_hash = transaction_hash
        self.__wallet_address = wallet_address
        self.__created_on = created_on
        self.__updated_on = updated_on
        self.__updated_by = updated_by
        self.__reviewed_by = reviewed_by
        self.__reviewed_on = reviewed_on

    def to_dict(self):
        state_dict = {
            "state": self.__state,
            "updated_on": "",
            "updated_by": self.__updated_by,
            "reviewed_by": self.__reviewed_by,
            "reviewed_on": ""
        }

        if self.__updated_on is not None:
            state_dict["updated_on"] = self.__updated_on.strftime("%Y-%m-%d %H:%M:%S")
        if self.__reviewed_on is not None:
            state_dict["reviewed_on"] = self.__reviewed_on.strftime("%Y-%m-%d %H:%M:%S")
        return state_dict
