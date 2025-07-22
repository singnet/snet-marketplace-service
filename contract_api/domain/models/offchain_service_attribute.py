from dataclasses import dataclass

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewOffchainServiceConfigDomain:
    org_id: str
    service_id: str
    parameter_name: str
    parameter_value: str


@dataclass
class OffchainServiceConfigDomain(NewOffchainServiceConfigDomain, BaseDomain):

    def to_attribute(self):
        return {
            self.parameter_name: self.parameter_value
        }
