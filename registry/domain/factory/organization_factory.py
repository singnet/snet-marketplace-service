from registry.domain.models.group import Group
from registry.domain.models.organization import Organization


class OrganizationFactory:

    @staticmethod
    def parse_raw_organization(payload):
        org_id = payload["org_id"]
        org_name = payload["org_name"]
        org_type = payload["org_type"]
        description = payload["description"]
        short_description = payload["description"]
        url = payload["url"]
        contacts = payload["contacts"]
        assets = payload["assets"]
        groups = OrganizationFactory.parse_raw_list_groups(payload["groups"])
        organization = Organization(org_name, org_id, org_type, description, short_description, url, contacts, assets)
        organization.add_all_groups(groups)
        return organization

    @staticmethod
    def parse_raw_list_groups(raw_groups):
        groups = []
        for group in raw_groups:
            groups.append(OrganizationFactory.parse_raw_group(group))
        return groups

    @staticmethod
    def parse_raw_group(raw_group):
        group_id = raw_group["id"]
        group_name = raw_group["name"]
        payment_address = raw_group["payment_address"]
        payment_config = raw_group["payment_config"]
        group = Group(group_name, group_id, payment_address, payment_config)
        return group