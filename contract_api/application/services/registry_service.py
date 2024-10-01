import os
import tempfile
import uuid
from pathlib import Path

from common.boto_utils import BotoUtils
from common.constant import BuildStatus
from common.utils import Utils, extract_zip_file, make_tarfile, download_file_from_url
from contract_api.config import REGION_NAME, ASSETS_COMPONENT_BUCKET_NAME
from contract_api.domain.factory.service_factory import ServiceFactory
from contract_api.domain.models.offchain_service_attribute import OffchainServiceAttributeEntityModel
from contract_api.infrastructure.repositories.service_repository import OffchainServiceConfigRepository

utils = Utils()
boto_utils = BotoUtils(region_name=REGION_NAME)
offchain_service_config_repo = OffchainServiceConfigRepository()
service_factory = ServiceFactory()


class RegistryService:
    def __init__(self, org_id, service_id):
        self.org_id = org_id
        self.service_id = service_id

    def save_offchain_service_attribute(self, new_offchain_attributes):
        updated_offchain_attributes = {}
        if "demo_component" in new_offchain_attributes:
            new_demo_component = ServiceFactory.create_demo_component_domain_model(
                new_offchain_attributes["demo_component"])
            # publish and update demo only on change_in_demo_component = 1 and required = 1
            if new_offchain_attributes["demo_component"].get("change_in_demo_component", 0) and \
                    new_demo_component.demo_component_required:
                new_demo_component.demo_component_url = self.publish_demo_component(
                    new_demo_component.demo_component_url
                )
                new_demo_component.demo_component_status = BuildStatus.PENDING
            # update and save new changes
            updated_offchain_attributes = OffchainServiceAttributeEntityModel(
                org_id=self.org_id,
                service_id=self.service_id,
                attributes=new_demo_component.to_dict()
            )
            offchain_service_attribute = offchain_service_config_repo.save_offchain_service_attribute(
                updated_offchain_attributes)
            updated_offchain_attributes = offchain_service_attribute.to_dict()
        return updated_offchain_attributes

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
        new_demo_url = f"https://{ASSETS_COMPONENT_BUCKET_NAME}.s3.amazonaws.com/{key}"
        return new_demo_url
