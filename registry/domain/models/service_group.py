class ServiceGroup:
    def __init__(self, org_uuid, service_uuid, group_id, endpoints, pricing):
        self.org_uuid = org_uuid
        self.service_uuid = service_uuid
        self.group_id = group_id
        self.endpoints = endpoints
        self.pricing = pricing

    def to_dict(self):
        return {
            "group_id": self.group_id,
            "endpoints": self.endpoints,
            "pricing": self.pricing
        }

    def to_metadata(self):
        return {
            "free_calls": 0,
            "free_call_signer_address": "",
            "daemon_address ": [],
            "pricing": self.pricing,
            "endpoints": self.endpoints,
            "group_id": self.group_id
        }
