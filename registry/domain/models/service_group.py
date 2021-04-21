from copy import deepcopy

class ServiceGroup:
    def __init__(self, org_uuid, service_uuid, group_id, group_name, endpoints, test_endpoints, pricing, free_calls,
                 daemon_address,
                 free_call_signer_address):
        self._org_uuid = org_uuid
        self._service_uuid = service_uuid
        self._group_id = group_id
        self._group_name = group_name
        self._endpoints = endpoints
        self._test_endpoints = test_endpoints
        self._pricing = pricing
        self._free_calls = free_calls
        self._free_call_signer_address = free_call_signer_address
        self._daemon_address = daemon_address

    def to_dict(self):
        return {
            "group_id": self._group_id,
            "group_name": self._group_name,
            "endpoints": self._endpoints,
            "test_endpoints": self._test_endpoints,
            "pricing": self._pricing,
            "free_calls": self._free_calls,
            "free_call_signer_address": self._free_call_signer_address,
            "daemon_addresses": self._daemon_address
        }

    def _get_endpoints(self):
        endpoints = []
        for endpoint, val in self._endpoints.items():
            endpoints.append(endpoint)
        return endpoints

    def to_metadata(self):
        return {
            "free_calls": self._free_calls,
            "free_call_signer_address": self._free_call_signer_address,
            "daemon_addresses": self._daemon_address,
            "pricing": deepcopy(self._pricing),
            "endpoints": self._get_endpoints(),
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

    @endpoints.setter
    def endpoints(self, endpoints):
        self._endpoints = endpoints

    @property
    def test_endpoints(self):
        return self._test_endpoints

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
