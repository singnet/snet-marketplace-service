import os
import tempfile
import uuid
from pathlib import Path
from typing import Any

from common.boto_utils import BotoUtils
from common.constant import BuildStatus
from common.utils import download_file_from_url, extract_zip_file, make_tarfile
from contract_api.application.schemas.service_schemas import GetServiceFiltersRequest, GetServicesRequest, \
    GetServiceRequest, CurateServiceRequest, SaveOffchainAttributeRequest, UpdateServiceRatingRequest
from contract_api.config import REGION_NAME, ASSETS_COMPONENT_BUCKET_NAME
from contract_api.constant import FilterKeys
from contract_api.domain.factory.service_factory import ServiceFactory
from contract_api.domain.models.demo_component import DemoComponent
from contract_api.domain.models.offchain_service_attribute import OffchainServiceConfigDomain
from contract_api.domain.models.org_group import OrgGroupDomain
from contract_api.domain.models.service_endpoint import ServiceEndpointDomain
from contract_api.domain.models.service_group import ServiceGroupDomain
from contract_api.infrastructure.repositories.organization_repository import OrganizationRepository
from contract_api.infrastructure.repositories.service_repository import ServiceRepository


class ServiceService:
    def __init__(self):
        self._service_repo = ServiceRepository()
        self._org_repo = OrganizationRepository()
        self._boto_utils = BotoUtils(region_name=REGION_NAME)

    def get_service_filters(self, request: GetServiceFiltersRequest) -> dict[str, list | dict]:
        attribute = request.attribute

        if attribute == FilterKeys.TAG_NAME:
            tags = self._service_repo.get_unique_service_tags()
            filters_data = [tag.tag_name for tag in tags]
        elif attribute == FilterKeys.ORG_ID:
            orgs = self._org_repo.get_organizations_with_curated_services()
            filters_data = {org.org_id: org.organization_name for org in orgs}
        else:
            filters_data = []

        return {"values": filters_data}

    def get_services(self, request: GetServicesRequest) -> dict[str, list | int]:
        limit = request.limit
        page = request.page
        sort = request.sort
        order = request.order
        filters = request.filter
        q = request.q

        services = self._service_repo.get_filtered_services(
            limit=limit,
            page=page,
            sort=sort,
            order=order,
            filters=filters,
            q=q
        )

        total_count = self._service_repo.get_filtered_services_count(
            filters=filters,
            q=q
        )

        return {
            "totalCount": total_count,
            "services": services
        }

    def get_service(self, request: GetServiceRequest) -> dict[str, Any]:
        org_id = request.org_id
        service_id = request.service_id

        service, organization, service_metadata = self._service_repo.get_service(
            org_id, service_id
        )
        service_media = self._service_repo.get_service_media(org_id, service_id)
        org_groups = self._org_repo.get_groups(org_id)
        groups_endpoints = self._service_repo.get_service_groups(org_id, service_id)
        service_tags = self._service_repo.get_service_tags(org_id, service_id)
        offchain_service_configs = self._service_repo.get_offchain_service_configs(org_id, service_id)

        service_data = service.to_short_response()
        service_data.update(organization.to_short_response())
        service_data.update(service_metadata.to_short_response())
        service_data["media"] = [media.to_short_response() for media in service_media]
        service_data["tags"] = [tag.tag_name for tag in service_tags]
        service_data.update(self._convert_service_groups(groups_endpoints, org_groups))
        service_data.update(self._get_demo_component_required(offchain_service_configs))

        return service_data

    def curate_service(self, request: CurateServiceRequest) -> dict:
        org_id = request.org_id
        service_id = request.service_id
        curate = request.curate
        self._service_repo.curate_service(org_id, service_id, curate)

        return {}

    def save_offchain_service_attribute(
            self, request: SaveOffchainAttributeRequest
    ) -> dict[str, str | dict]:
        org_id = request.org_id
        service_id = request.service_id
        demo_component_dict = request.demo_component
        demo_component = DemoComponent(demo_component_dict)

        if demo_component.demo_component_required == 1 and demo_component.change_in_demo_component:
            demo_component.demo_component_url = self._publish_demo_component(
                org_id,
                service_id,
                demo_component.demo_component_url
            )
            demo_component.demo_component_status = BuildStatus.PENDING

        updated_offchain_attributes = ServiceFactory.offchain_service_configs_from_demo_component(demo_component)
        self._service_repo.upsert_offchain_service_config(org_id, service_id, updated_offchain_attributes)

        attributes = {}
        for config in updated_offchain_attributes:
            attributes.update(config.to_attribute())

        return {"org_id": org_id, "service_id": service_id, "attributes": attributes}

    def update_service_rating(self, request: UpdateServiceRatingRequest) -> dict:
        org_id = request.org_id
        service_id = request.service_id
        rating = request.rating
        total_users_rated = request.total_users_rated

        service_rating = {
            "rating": rating,
            "total_users_rated": total_users_rated
        }
        self._service_repo.update_service_rating(org_id, service_id, service_rating)

        return {"org_id": org_id, "service_id": service_id, "rating": service_rating}

    @staticmethod
    def _convert_service_groups(
            groups_endpoints: list[tuple[ServiceGroupDomain, ServiceEndpointDomain]],
            org_groups: list[OrgGroupDomain]
    ) -> dict[str, int | list]:
        org_group_dict = {group.group_id: group.to_short_response() for group in org_groups}

        result = {
            "isAvailable": False,
            "groups": [],
        }

        for group, endpoint in groups_endpoints:
            item = group.to_short_response()
            item["endpoints"] = [endpoint.to_short_response()]
            item.update(org_group_dict[group.group_id])
            result["groups"].append(item)
            if endpoint.is_available:
                result["isAvailable"] = True

        return result

    @staticmethod
    def _get_demo_component_required(
            offchain_service_configs: list[OffchainServiceConfigDomain]
    ) -> dict:
        for config in offchain_service_configs:
            if config.parameter_name == "demo_component_required":
                return {"demoComponentRequired": config.parameter_value == "1"}
        return {"demoComponentAvailable": False}

    def _publish_demo_component(self, org_id, service_id, demo_file_url):
        root_directory = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        if not Path.exists(Path(root_directory)):
            os.mkdir(root_directory)
        component_name = download_file_from_url(demo_file_url, root_directory)

        extracted_file = os.path.join(root_directory, component_name.split(".")[0].split("_")[1])
        extract_zip_file(os.path.join(root_directory, component_name), extracted_file)

        output_path = os.path.join(root_directory, component_name.split(".")[0].split("_")[1] + '.tar.gz')
        make_tarfile(source_dir = extracted_file, output_filename = output_path)

        key = f"assets/{org_id}/{service_id}/component.tar.gz"
        self._boto_utils.s3_upload_file(filename = output_path, bucket = ASSETS_COMPONENT_BUCKET_NAME, key = key)
        new_demo_url = f"https://{ASSETS_COMPONENT_BUCKET_NAME}.s3.amazonaws.com/{key}"
        return new_demo_url
