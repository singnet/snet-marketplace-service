class Service:
    def __init__(self, org_uuid, uuid, service_id, display_name, short_description, description, project_url, proto,
                 assets, ranking, rating, contributors, metadata_ipfs_hash, groups, state):
        self.org_uuid = org_uuid
        self.uuid = uuid
        self.service_id = service_id
        self.display_name = display_name
        self.short_description = short_description
        self.description = description
        self.project_url = project_url
        self.proto = proto
        self.assets = assets
        self.ranking = ranking
        self.rating = rating
        self.contributors = contributors
        self.metadata_ipfs_hash = metadata_ipfs_hash
        self.state = state
        self.groups = groups

    def to_dict(self):
        return {
            "org_uuid": self.org_uuid,
            "service_uuid": self.uuid,
            "display_name": self.display_name,
            "state": self.state,
            "short_description": self.short_description,
            "description": self.description,
            "project_url": self.project_url,
            "proto": self.proto,
            "assets": self.assets,
            "ranking": self.ranking,
            "rating": self.rating,
            "contributors": self.contributors,
            "metadata_ipfs_hash": self.metadata_ipfs_hash,
            "groups": [group.to_dict() for group in self.groups]
        }

    def to_metadata(self):
        return {
            "version": 1,
            "display_name": self.display_name,
            "encoding": self.proto.get("encoding", ""),
            "service_type": self.proto.get("service_type", ""),
            "model_ipfs_hash": self.proto.get("model_ipfs_hash", ""),
            "mpe_address": "",
            "groups": [group.to_dict() for group in self.groups],
            "assets": self.assets,
            "service_description": self.description,
            "contributors": self.contributors
        }
