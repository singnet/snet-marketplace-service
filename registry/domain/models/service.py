class Service:
    def __init__(self, org_uuid, uuid, service_id, display_name, short_description, description, project_url, proto,
                 assets, ranking, rating, contributors, tags, mpe_address, metadata_ipfs_hash, groups, service_state):
        self._org_uuid = org_uuid
        self._uuid = uuid
        self._service_id = service_id
        self._display_name = display_name
        self._short_description = short_description
        self._description = description
        self._project_url = project_url
        self._proto = proto
        self._assets = assets
        self._ranking = ranking
        self._rating = rating
        self._contributors = contributors
        self._tags = tags
        self._mpe_address = mpe_address
        self._metadata_ipfs_hash = metadata_ipfs_hash
        self._groups = groups
        self._service_state = service_state

    def to_response(self):
        return {
            "org_uuid": self._org_uuid,
            "service_uuid": self._uuid,
            "service_id": self._service_id,
            "display_name": self._display_name,
            "short_description": self._short_description,
            "description": self._description,
            "project_url": self._project_url,
            "proto": self._proto,
            "assets": self._assets,
            "ranking": self._ranking,
            "rating": self._rating,
            "contributors": self._contributors,
            "tags": self._tags,
            "mpe_address": self._mpe_address,
            "metadata_ipfs_hash": self._metadata_ipfs_hash,
            "groups": [group.to_response() for group in self._groups],
            "service_state": self._service_state.to_response()
        }

    def to_metadata(self):
        return {
            "version": 1,
            "display_name": self._display_name,
            "encoding": self.proto.get("encoding", ""),
            "service_type": self.proto.get("service_type", ""),
            "model_ipfs_hash": self.proto.get("model_ipfs_hash", ""),
            "mpe_address": self._mpe_address,
            "groups": [group.to_metadata() for group in self._groups],
            "service_description": {
                "url": self._project_url,
                "short_description": self.short_description,
                "description": self._description
            },
            "assets": self._assets,
            "contributors": self._contributors
        }

    @property
    def org_uuid(self):
        return self._org_uuid

    @property
    def uuid(self):
        return self._uuid

    @property
    def service_id(self):
        return self._service_id

    @property
    def display_name(self):
        return self._display_name

    @property
    def short_description(self):
        return self._short_description

    @property
    def description(self):
        return self._description

    @property
    def project_url(self):
        return self._project_url

    @property
    def proto(self):
        return self._proto

    @proto.setter
    def proto(self, proto):
        self._proto = proto

    @property
    def assets(self):
        return self._assets

    @assets.setter
    def assets(self, assets):
        self._assets = assets

    @property
    def ranking(self):
        return self._ranking

    @property
    def rating(self):
        return self._rating

    @property
    def contributors(self):
        return self._contributors

    @property
    def metadata_ipfs_hash(self):
        return self._metadata_ipfs_hash

    @metadata_ipfs_hash.setter
    def metadata_ipfs_hash(self, metadata_ipfs_hash):
        self._metadata_ipfs_hash = metadata_ipfs_hash

    @property
    def groups(self):
        return [group for group in self._groups]

    @property
    def service_state(self):
        return self._service_state

    @service_state.setter
    def service_state(self, service_state):
        self._service_state = service_state

    @property
    def tags(self):
        return self._tags

    @property
    def mpe_address(self):
        return self._mpe_address
