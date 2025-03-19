from datetime import datetime
from uuid import uuid4

from registry.migration.config import ORIGIN
from registry.migration.domain.models.organization import Organization, OrganizationMember, Group
from registry.migration.domain.models.service import Service, ServiceGroup


class OrganizationMapper:

    @staticmethod
    def org_from_old_org(old_org):
        org_uuid = uuid4().hex
        org_id = old_org.org_id
        name = old_org.organization_name
        org_type = ""
        origin = ORIGIN

        description = old_org.description
        if isinstance(description, dict):
            long_description = description.get("description", "")
            short_description = description.get("short_description", "")
            url = description.get("url", "")
        else:
            long_description = ""
            short_description = ""
            url = ""

        contacts = old_org.contacts
        assets_urls = old_org.org_assets_url
        assets_hash = old_org.assets_hash
        assets = OrganizationMapper.assets_from_ord_org_assets(assets_urls, assets_hash)
        metadata_ipfs_uri = old_org.org_metadata_uri
        duns_no = ""
        current_time = datetime.utcnow()
        members = [OrganizationMember(
            org_uuid=org_uuid, username=None, status="PUBLISHED", role="OWNER",
            address=old_org.owner_address, invite_code=None, transaction_hash=None, invited_on=None,
            updated_on=current_time, created_on=current_time)]
        return Organization(org_uuid, org_id, name, org_type, origin, long_description, short_description, url,
                            contacts, assets, metadata_ipfs_uri, duns_no, members, [])

    @staticmethod
    def assets_from_ord_org_assets(assets_urls, assets_hash):
        assets = {}
        for key in assets_urls.keys():
            if key not in assets:
                assets[key] = {}
            assets[key]["url"] = assets_urls[key]

        for key in assets_hash.keys():
            if key not in assets:
                assets[key] = {}
            assets[key]["ipfs_hash"] = assets_hash[key]

        if "hero_image" not in assets:
            assets["hero_image"] = {
                "url": "",
                "ipfs_hash": ""
            }
        return assets

    @staticmethod
    def org_list_from_old_org(old_org_list):
        return [OrganizationMapper.org_from_old_org(org) for org in old_org_list]

    @staticmethod
    def group_from_old_group(old_group):
        name = old_group.group_name
        group_id = old_group.group_id
        org_id = old_group.org_id
        created_at = old_group.row_created
        updated_at = old_group.row_updated
        payment = old_group.payment
        payment_address = payment["payment_address"]
        payment.pop("payment_address")
        status = ""
        return Group(name, "", org_id, group_id, payment_address, payment, status, created_at, updated_at)

    @staticmethod
    def groups_from_old_group_list(org_groups_list):
        return [OrganizationMapper.group_from_old_group(group) for group in org_groups_list]


class ServiceMapper:

    @staticmethod
    def service_from_old_service_list(old_service_list):
        return [ServiceMapper.service_from_old_service(service) for service in old_service_list]

    @staticmethod
    def service_from_old_service(old_service):
        org_uuid = ""
        org_id = old_service.ServiceMetadata.org_id
        uuid = uuid4().hex
        display_name = old_service.ServiceMetadata.display_name
        service_id = old_service.ServiceMetadata.service_id

        metadata_uri = old_service.Service.ipfs_hash
        if not metadata_uri.startswith("ipfs://"):
            metadata_uri = f"ipfs://{metadata_uri}"

        proto = {
            "encoding": old_service.ServiceMetadata.encoding,
            "service_type": old_service.ServiceMetadata.type,
            "model_hash": old_service.ServiceMetadata.model_ipfs_hash
        }
        short_description = old_service.ServiceMetadata.short_description
        description = old_service.ServiceMetadata.description
        project_url = old_service.ServiceMetadata.url
        assets_url = old_service.ServiceMetadata.assets_url
        assets_hash = old_service.ServiceMetadata.assets_hash

        assets = {
            "hero_image": {
                "url": assets_url.get("hero_image", ""),
                "ipfs_hash": assets_hash.get("hero_image", "")
            },
            "proto_files": {
                "url": "",
                "ipfs_hash": ""
            },
            "demo_files": {
                "url": "",
                "ipfs_hash": ""
            }
        }

        rating = old_service.ServiceMetadata.service_rating
        ranking = old_service.ServiceMetadata.ranking

        if isinstance(old_service.ServiceMetadata.contributors, list):
            contributors = old_service.ServiceMetadata.contributors
        else:
            contributors = []
        mpe_address = old_service.ServiceMetadata.mpe_address

        return Service(org_id, org_uuid, service_id, uuid, display_name, metadata_uri, proto, short_description,
                       description, project_url, assets, rating, ranking, contributors, [], mpe_address, [], None)

    @staticmethod
    def group_from_old_group_list(old_group_list):
        return [ServiceMapper.group_from_old_group(group) for group in old_group_list]

    @staticmethod
    def group_from_old_group(old_group):
        org_id = old_group.org_id
        service_id = old_group.service_id
        service_uuid = ""
        org_uuid = ""
        group_id = old_group.group_id
        group_name = old_group.group_name
        pricing = old_group.pricing
        endpoints = []
        test_endpoints = []
        daemon_address = []
        free_calls = 15
        free_call_signer_address = ""
        return ServiceGroup(org_id, org_uuid, service_id, service_uuid, group_id, group_name, pricing, endpoints,
                            test_endpoints, daemon_address, free_calls, free_call_signer_address)
