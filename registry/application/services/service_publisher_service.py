import json
import requests
import glob
import tarfile
import os
import io
from zipfile import ZipFile
from urllib.parse import urlparse
from registry.infrastructure.repositories.service_repository import ServiceRepository
from registry.constants import ServiceAvailabilityStatus, ServiceStatus, DEFAULT_SERVICE_RANKING
from registry.config import IPFS_URL, METADATA_FILE_PATH, ASSET_DIR
from uuid import uuid4
from registry.exceptions import InvalidServiceState, ServiceProtoNotFoundException
from registry.domain.factory.service_factory import ServiceFactory
from registry.domain.models.service_state import ServiceState
from common.ipfs_util import IPFSUtil
from common.utils import json_to_file, hash_to_bytesuri
from common.constant import StatusCode
from common.logger import get_logger

ALLOWED_ATTRIBUTES_FOR_SERVICE_SEARCH = ["display_name"]
DEFAULT_ATTRIBUTE_FOR_SERVICE_SEARCH = "display_name"
ALLOWED_ATTRIBUTES_FOR_SERVICE_SORT_BY = ["ranking", "service_id"]
DEFAULT_ATTRIBUTES_FOR_SERVICE_SORT_BY = "ranking"
ALLOWED_ATTRIBUTES_FOR_SERVICE_ORDER_BY = ["asc", "desc"]
DEFAULT_ATTRIBUTES_FOR_SERVICE_ORDER_BY = "desc"
DEFAULT_OFFSET = 0
DEFAULT_LIMIT = 0

logger = get_logger(__name__)


class ServicePublisherService:
    def __init__(self, username, org_uuid, service_uuid):
        self.username = username
        self.org_uuid = org_uuid
        self.service_uuid = service_uuid

    def get_service_id_availability_status(self, service_id):
        record_exist = ServiceRepository().check_service_id_within_organization(self.org_uuid, service_id)
        if record_exist:
            return ServiceAvailabilityStatus.UNAVAILABLE.value
        return ServiceAvailabilityStatus.AVAILABLE.value

    def save_service(self, payload):
        service = ServiceFactory().create_service_entity_model(self.org_uuid, self.service_uuid, payload,
                                                               ServiceStatus.DRAFT.value)
        service = ServiceRepository().save_service(self.username, service, ServiceStatus.DRAFT.value)
        return service.to_response()

    def save_transaction_hash_for_published_service(self, payload):
        service = ServiceRepository().get_service_for_given_service_uuid(self.org_uuid, self.service_uuid)
        if service.service_state.state == ServiceStatus.APPROVED.value:
            service.service_state = \
                ServiceFactory().create_service_state_entity_model(
                    self.org_uuid, self.service_uuid, ServiceStatus.PUBLISH_IN_PROGRESS.value,
                    payload.get("transaction_hash", ""))
            ServiceRepository().save_service(self.username, service, ServiceStatus.PUBLISH_IN_PROGRESS.value)
        return StatusCode.OK

    def submit_service_for_approval(self, payload):
        service = ServiceFactory().create_service_entity_model(self.org_uuid, self.service_uuid, payload,
                                                               ServiceStatus.APPROVAL_PENDING.value)
        service = ServiceRepository().save_service(self.username, service, ServiceStatus.APPROVAL_PENDING.value)
        return service.to_response()

    def create_service(self, payload):
        service_uuid = uuid4().hex
        service = ServiceFactory().create_service_entity_model(self.org_uuid, service_uuid, payload,
                                                               ServiceStatus.DRAFT.value)
        ServiceRepository().add_service(service, self.username)
        return {"org_uuid": self.org_uuid, "service_uuid": service_uuid}

    def get_services_for_organization(self, payload):
        offset = payload.get("offset", DEFAULT_OFFSET)
        limit = payload.get("limit", DEFAULT_LIMIT)
        search_string = payload["q"]
        search_attribute = payload["s"]
        sort_by = payload["sort_by"].lower()
        order_by = payload["order_by"].lower()
        filter_parameters = {
            "offset": offset,
            "limit": limit,
            "search_string": search_string,
            "search_attribute": search_attribute if search_attribute in ALLOWED_ATTRIBUTES_FOR_SERVICE_SEARCH else DEFAULT_ATTRIBUTE_FOR_SERVICE_SEARCH,
            "sort_by": sort_by if sort_by in ALLOWED_ATTRIBUTES_FOR_SERVICE_SORT_BY else DEFAULT_ATTRIBUTES_FOR_SERVICE_SORT_BY,
            "order_by": order_by if order_by in ALLOWED_ATTRIBUTES_FOR_SERVICE_SORT_BY else DEFAULT_ATTRIBUTES_FOR_SERVICE_ORDER_BY
        }
        search_result = ServiceRepository().get_services_for_organization(self.org_uuid, filter_parameters)
        search_count = ServiceRepository().get_total_count_of_services_for_organization(self.org_uuid,
                                                                                        filter_parameters)
        return {"total_count": search_count, "offset": offset, "limit": limit, "result": search_result}

    def get_service_for_given_service_uuid(self):
        service = ServiceRepository().get_service_for_given_service_uuid(self.org_uuid, self.service_uuid)
        return service.to_response()

    def publish_service_data_to_ipfs(self):
        service = ServiceRepository().get_service_for_given_service_uuid(self.org_uuid, self.service_uuid)
        if service.service_state.state == ServiceStatus.APPROVED.value:
            service = self.publish_proto_files_in_ipfs(service)
            service_metadata = service.to_metadata()
            filename = f"{METADATA_FILE_PATH}/{service.uuid}_service_metadata.json"
            service.metadata_ipfs_hash = ServicePublisherService.publish_to_ipfs(filename, service_metadata)
            return {"service_metadata": service.to_metadata(),
                    "metadata_ipfs_hash": "ipfs://"+service.metadata_ipfs_hash}
        logger.info(f"Service status needs to be {ServiceStatus.APPROVED.value} to be eligible for publishing.")
        raise InvalidServiceState()

    def publish_proto_files_in_ipfs(self, service):
        proto_url = service.assets.get("proto_files", {}).get("url", None)
        if proto_url is None:
            raise ServiceProtoNotFoundException
        ipfs_client = IPFSUtil(IPFS_URL['url'], IPFS_URL['port'])
        asset_ipfs_hash = self.publish_proto_in_ipfs(ipfs_client, proto_url,
                                                     f"{ASSET_DIR}/{service.org_uuid}/{service.uuid}")
        service.assets["proto_files"]["ipfs_hash"] = asset_ipfs_hash
        service.proto = {
            "model_ipfs_hash": asset_ipfs_hash,
            "encoding": "proto",
            "service_type": "grpc"
        }
        service = ServiceRepository().save_service(self.username, service, service.service_state.state)
        return service

    @staticmethod
    def publish_proto_in_ipfs(ipfs_client, proto_url, proto_dir):
        response = requests.get(proto_url)
        filename = urlparse(proto_url).path.split("/")[-1]
        if not os.path.exists(proto_dir):
            os.makedirs(proto_dir)
        with open(f"{proto_dir}/{filename}", 'wb') as asset_file:
            asset_file.write(response.content)
        with ZipFile(f"{proto_dir}/{filename}", 'r') as zipObj:
            listOfFileNames = zipObj.namelist()
            zipObj.extractall(proto_dir, listOfFileNames)
        if not os.path.isdir(proto_dir):
            raise Exception("Directory %s doesn't exists" % proto_dir)
        files = glob.glob(os.path.join(proto_dir, "*.proto"))
        if len(files) == 0:
            raise Exception("Cannot find any %s files" % (os.path.join(proto_dir, "*.proto")))
        files.sort()
        tar_bytes = io.BytesIO()
        tar = tarfile.open(fileobj=tar_bytes, mode="w")
        for f in files:
            tar.add(f, os.path.basename(f))
        tar.close()
        return ipfs_client.ipfs_conn.add_bytes(tar_bytes.getvalue())

    @staticmethod
    def publish_to_ipfs(filename, data):
        json_to_file(data, filename)
        service_metadata_ipfs_hash = IPFSUtil(
            IPFS_URL['url'], IPFS_URL['port']).write_file_in_ipfs(filename, wrap_with_directory=False)
        return service_metadata_ipfs_hash
