class ServiceGroup:
    def __init__(self):
        self.org_uuid = None
        self.service_uuid = None
        self.group_id = None
        self.endpoints = None
        self.pricing = None

    def to_dict(self):
        return {
            "org_uuid": self.org_uuid,
            "service_uuid": self.service_uuid,
            "groups": {
                "group_id": self.group_id,
                "endpoints": self.endpoints,
                "pricing": self.pricing
            }
        }
