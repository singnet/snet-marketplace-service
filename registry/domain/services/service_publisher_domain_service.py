from typing import Dict

from common.ipfs_util import IPFSUtil
from common.logger import get_logger
from common.utils import publish_zip_file_in_ipfs, publish_file_in_ipfs
from registry.config import ASSET_DIR, IPFS_URL
from registry.domain.factory.service_factory import ServiceFactory
from registry.exceptions import InvalidMetadataException
from registry.domain.models.service import Service as ServiceEntityModel

service_factory = ServiceFactory()
ipfs_client = IPFSUtil(IPFS_URL['url'], IPFS_URL['port'])
logger = get_logger(__name__)
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

    def publish_service_assets(self, service_assets: dict) -> Dict[str, str]:
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
    def get_service_metadata(service: ServiceEntityModel) -> dict:
        service_metadata = service.to_metadata()
        if not service.is_metadata_valid(service_metadata):
            logger.info("Service metadata is not valid")
            raise InvalidMetadataException()
        return service_metadata

    @staticmethod
    def publish_assets(service: ServiceEntityModel):
        ASSETS_SUPPORTED = ["hero_image", "demo_files"]
        for asset in service.assets.keys():
            if asset in ASSETS_SUPPORTED:
                asset_url = service.assets.get(asset, {}).get("url", None)
                if asset_url is None:
                    logger.info(f"asset url for {asset} is missing ")
                asset_ipfs_hash = publish_file_in_ipfs(file_url=asset_url,
                                                       file_dir=f"{ASSET_DIR}/{service.org_uuid}/{service.uuid}",
                                                       ipfs_client=IPFSUtil(IPFS_URL['url'], IPFS_URL['port']))
                service.assets[asset]["ipfs_hash"] = asset_ipfs_hash
