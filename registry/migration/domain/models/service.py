class Service:
    def __init__(self, org_id, org_uuid, service_id, uuid, display_name, metadata_uri, proto, short_description, description,
                 project_url, assets, rating, ranking, contributors, tags, mpe_address, groups, service_state):
        self.org_id = org_id
        self.org_uuid = org_uuid
        self.uuid = uuid
        self.display_name = display_name
        self.service_id = service_id
        self.metadata_uri = metadata_uri
        self.proto = proto
        self.short_description = short_description
        self.description = description
        self.project_url = project_url
        self.assets = assets
        self.rating = rating
        self.ranking = ranking
        self.contributors = contributors
        self.tags = tags
        self.mpe_address = mpe_address
        self.groups = groups
        self.service_state = service_state


class ServiceGroup:
    def __init__(self, org_id, org_uuid, service_id, service_uuid, group_id, group_name, pricing, endpoints,
                 test_endpoints, daemon_address, free_calls, free_call_signer_address):
        self.org_id = org_id
        self.org_uuid = org_uuid
        self.service_id = service_id
        self.service_uuid = service_uuid
        self.group_id = group_id
        self.group_name = group_name
        self.pricing = pricing
        self.endpoints = endpoints
        self.test_endpoints = test_endpoints
        self.daemon_address = daemon_address
        self.free_calls = free_calls
        self.free_call_signer_address = free_call_signer_address
