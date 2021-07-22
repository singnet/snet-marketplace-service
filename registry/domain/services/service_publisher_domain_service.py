import filecmp
import os
import shutil
import tempfile
import uuid
from common import utils
from common.ipfs_util import IPFSUtil
from common.logger import get_logger
from common.utils import json_to_file, publish_zip_file_in_ipfs, publish_file_in_ipfs, download_file_from_url
from registry.config import ASSET_DIR, METADATA_FILE_PATH, IPFS_URL
from registry.domain.factory.service_factory import ServiceFactory
from registry.domain.services.registry_blockchain_util import RegistryBlockChainUtil
from registry.exceptions import ServiceProtoNotFoundException, InvalidMetadataException
ipfs_util = IPFSUtil(IPFS_URL["url"], IPFS_URL["port"])

service_factory = ServiceFactory()
ipfs_client = IPFSUtil(IPFS_URL['url'], IPFS_URL['port'])
logger = get_logger(__name__)
METADATA_URI_PREFIX = "ipfs://"
SERVICE_ASSETS_SUPPORTED = {
    "proto_files": {
        "required": True
    },
    "hero_image": {
        "required": False
    },
    "demo_files": {
        "required": False

    }
}


class ServicePublisherDomainService:
    def __init__(self, username, org_uuid, service_uuid):
        self._username = username
        self._org_uuid = org_uuid
        self._service_uuid = service_uuid

    def publish_service_assets(self, service_assets):
        assets_url_ipfs_hash_dict = {}
        for asset in service_assets.keys():
            if asset in SERVICE_ASSETS_SUPPORTED.keys():
                asset_url = service_assets.get(asset, {}).get("url", None)
                if bool(asset_url):
                    logger.info(f"asset url for {asset} is missing ")
                    if SERVICE_ASSETS_SUPPORTED[asset]["required"]:
                        raise Exception(f"ASSET {asset} NOT FOUND")
                asset_ipfs_hash = publish_zip_file_in_ipfs(file_url=asset_url,
                                                           file_dir=f"{ASSET_DIR}/{self._org_uuid}/{self._service_uuid}",
                                                           ipfs_client=IPFSUtil(IPFS_URL['url'], IPFS_URL['port']))
                assets_url_ipfs_hash_dict[asset] = {
                    "ipfs_hash": asset_ipfs_hash,
                    "url": asset_url
                }
        return assets_url_ipfs_hash_dict

    @staticmethod
    def publish_service_proto_to_ipfs(service):
        proto_url = service.assets.get("proto_files", {}).get("url", None)
        if proto_url is None:
            raise ServiceProtoNotFoundException
        proto_ipfs_hash = utils.publish_file_in_ipfs(file_url=proto_url,
                                                     file_dir=f"{ASSET_DIR}/{service.org_uuid}/{service.uuid}",
                                                     ipfs_client=ipfs_client)
        service.proto = {
            "model_ipfs_hash": proto_ipfs_hash,
            "encoding": "proto",
            "service_type": "grpc"
        }
        service.assets["proto_files"]["ipfs_hash"] = proto_ipfs_hash
        return service

    @staticmethod
    def publish_file_to_ipfs(filename):
        metadata_ipfs_hash = ipfs_client.write_file_in_ipfs(filename, wrap_with_directory=False)
        return metadata_ipfs_hash

    def validate_service_metadata(self):
        pass

    def publish_service_data_to_ipfs(self, service, environment):
        # publish assets
        service = self.publish_service_proto_to_ipfs(service)
        self.publish_assets(service)
        service_metadata = self.get_service_metadata(service, environment)
        service_metadata_filename = f"{METADATA_FILE_PATH}/{service.uuid}_service_metadata.json"
        json_to_file(service_metadata, service_metadata_filename)
        service.metadata_uri = METADATA_URI_PREFIX + self.publish_file_to_ipfs(service_metadata_filename)
        return service

    @staticmethod
    def get_service_metadata(service, environment):
        service_metadata = service.to_metadata()
        if not service.is_metadata_valid(service_metadata):
            logger.info("Service metadata is not valid")
            raise InvalidMetadataException()
        return service_metadata

    def publish_service_on_blockchain(self, org_id, service, environment):
        # deploy service on testing blockchain environment for verification
        transaction_hash = RegistryBlockChainUtil(environment).register_or_update_service_in_blockchain(
            org_id=org_id, service_id=service.service_id,
            metadata_uri=service.metadata_uri)
        return service.to_dict()

    @staticmethod
    def publish_assets(service, existing_proto_hash):
        try:
            ASSETS_SUPPORTED = ["hero_image", "proto_files", "demo_files"]
            base_dir = f"{ASSET_DIR}/{service.org_uuid}/{service.uuid}"
            for asset in service.assets.keys():
                if asset in ASSETS_SUPPORTED:
                    asset_url = service.assets.get(asset, {}).get("url", None)
                    if asset_url is None:
                        logger.info(f"asset url for {asset} is missing ")
                    if asset == "proto_files":
                        if not ServicePublisherDomainService.get_proto_diff(asset_url, existing_proto_hash):
                            service.assets[asset]["ipfs_hash"] = existing_proto_hash
                            continue
                    asset_ipfs_hash = publish_file_in_ipfs(
                        file_url=asset_url,
                        file_dir=f"{base_dir}/{asset}",
                        ipfs_client=IPFSUtil(IPFS_URL['url'], IPFS_URL['port']))
                    service.assets[asset]["ipfs_hash"] = asset_ipfs_hash
        except Exception as e:
            raise e
        finally:
            if os.path.exists(base_dir):
                shutil.rmtree(base_dir)

    @staticmethod
    def get_proto_diff(proto_url, existing_proto_hash):
        try:
            base_dir = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
            current_proto = download_file_from_url(proto_url, base_dir)
            published_proto = ipfs_util.read_bytesio_from_ipfs(existing_proto_hash)
            with open(os.path.join(base_dir, "proto.tar"), 'wb') as outfile:
                outfile.write(published_proto.getbuffer())
            current_proto_files = utils.extract_zip_file(os.path.join(base_dir, current_proto), os.path.join(base_dir, "proto_old"))
            published_proto_files = utils.extract_zip_file(os.path.join(base_dir, 'proto.tar'), os.path.join(base_dir, 'proto_new'))
            file_diff = utils.compare_directory(current_proto_files, published_proto_files)
            return file_diff
        finally:
            if os.path.exists(base_dir):
                shutil.rmtree(base_dir)