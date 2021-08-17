import os
import tempfile
import uuid
from datetime import datetime as dt
from pathlib import Path

from common.utils import Utils, extract_zip_file, make_tarfile, download_file_from_url
from common.boto_utils import BotoUtils
from contract_api.config import REGION_NAME, ASSETS_COMPONENT_BUCKET_NAME
from contract_api.domain.models.offchain_service_attribute import OffchainServiceAttribute
from contract_api.infrastructure.repositories.service_repository import OffchainServiceConfigRepository

utils = Utils()
boto_utils = BotoUtils(region_name=REGION_NAME)
offchain_service_config_repo = OffchainServiceConfigRepository()


class RegistryService:
    def __init__(self, org_id, service_id):
        self.org_id = org_id
        self.service_id = service_id

    def save_offchain_service_attribute(self, attributes):
        attributes = self.publish_offline_assets(attributes)
        offchain_service_attribute = OffchainServiceAttribute(org_id=self.org_id, service_id=self.service_id,
                                                              attributes=attributes)
        offchain_service_attribute = offchain_service_config_repo.save_offchain_service_attribute(
            offchain_service_attribute)
        return offchain_service_attribute.to_dict()

    def publish_offline_assets(self, attributes):
        # publish demo component file
        if attributes.get("demo_component_url", ""):
            new_demo_url = self.publish_demo_component(attributes["demo_component_url"])
            attributes.update({"demo_component_status": "PENDING"})
            attributes.update({"demo_component_url": new_demo_url})
            attributes.update({"demo_component_last_updated": str(dt.utcnow())})
        return attributes

    def publish_demo_component(self, demo_file_url):
        # download zip component file
        root_directory = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        if not Path.exists(Path(root_directory)):
            os.mkdir(root_directory)
        component_name = download_file_from_url(demo_file_url, root_directory)

        # extract the zip file
        extracted_file = os.path.join(root_directory, component_name.split(".")[0].split("_")[1])
        extract_zip_file(os.path.join(root_directory, component_name), extracted_file)
        # prepare tar file
        output_path = os.path.join(root_directory, component_name.split(".")[0].split("_")[1] + '.tar.gz')
        make_tarfile(source_dir=extracted_file, output_filename=output_path)

        # upload demo file to s3 and demo attributes
        key = f"assets/{self.org_id}/{self.service_id}/component.tar.gz"
        boto_utils.s3_upload_file(filename=output_path, bucket=ASSETS_COMPONENT_BUCKET_NAME, key=key)
        return f"https://{ASSETS_COMPONENT_BUCKET_NAME}.s3.amazonaws.com/{key}"
