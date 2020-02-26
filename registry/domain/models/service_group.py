class ServiceGroup:
    def __init__(self, org_uuid, service_uuid, group_id, group_name, endpoints, pricing, free_calls, daemon_address,
                 free_call_signer_address):
        self._org_uuid = org_uuid
        self._service_uuid = service_uuid
        self._group_id = group_id
        self._group_name = group_name
        self._endpoints = endpoints
        self._pricing = pricing
        self._free_calls = free_calls
        self._free_call_signer_address = free_call_signer_address
        self._daemon_address = daemon_address

    def to_response(self):
        return {
            "group_id": self._group_id,
            "group_name": self._group_name,
            "endpoints": self._endpoints,
            "pricing": self._pricing,
            "free_calls": self._free_calls,
            "free_call_signer_address": self._free_call_signer_address,
            "daemon_address ": self._daemon_address
        }

    def to_metadata(self):
        return {
            "free_calls": self._free_calls,
            "free_call_signer_address": self._free_call_signer_address,
            "daemon_address ": self._daemon_address,
            "pricing": self._pricing,
            "endpoints": self._endpoints,
            "group_id": self._group_id,
            "group_name": self._group_name
        }

    @property
    def org_uuid(self):
        return self._org_uuid

    @property
    def service_uuid(self):
        return self._service_uuid

    @property
    def group_id(self):
        return self._group_id

    @property
    def group_name(self):
        return self._group_name

    @property
    def endpoints(self):
        return self._endpoints

    @property
    def pricing(self):
        return self._pricing

    @property
    def daemon_address(self):
        return self._daemon_address

    @property
    def free_calls(self):
        return self._free_calls

    @property
    def free_call_signer_address(self):
        return self._free_call_signer_address
