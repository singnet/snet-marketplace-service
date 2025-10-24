from dataclasses import dataclass

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewOrganizationDomain:
    org_id: str
    organization_name: str
    owner_address: str
    org_metadata_uri: str
    org_assets_url: dict
    is_curated: bool
    description: dict
    assets_hash: dict
    contacts: dict


@dataclass
class OrganizationDomain(NewOrganizationDomain, BaseDomain):
    org_email: str

    def to_short_response(self) -> dict:
        support_contacts = {
            "email": "",
            "phone": "",
        }
        for contact in self.contacts:
            if contact["contact_type"] == "support":
                support_contacts["email"] = contact["email"]
                support_contacts["phone"] = contact["phone"]
                break
        return {
            "orgId": self.org_id,
            "organizationName": self.organization_name,
            "orgImageUrl": self.org_assets_url.get("hero_image", ""),
            "supportContacts": support_contacts
        }
