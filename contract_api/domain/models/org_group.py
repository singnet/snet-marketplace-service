from dataclasses import dataclass

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewOrgGroupDomain:
    org_id: str
    group_id: str
    group_name: str
    payment: dict


@dataclass
class OrgGroupDomain(NewOrgGroupDomain, BaseDomain):

    def to_short_response(self) -> dict:
        return {
            "groupId": self.group_id,
            "groupName": self.group_name,
            "payment": self.payment,
        }