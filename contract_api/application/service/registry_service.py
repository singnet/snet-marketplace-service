import os
import tempfile
import uuid
from datetime import datetime as dt
from pathlib import Path

from common.boto_utils import BotoUtils
from common.constant import BuildStatus
from common.utils import Utils, extract_zip_file, make_tarfile, download_file_from_url
from contract_api.config import REGION_NAME, ASSETS_COMPONENT_BUCKET_NAME
from contract_api.domain.factory.service_factory import ServiceFactory
from contract_api.domain.models.demo_component import DemoComponent
from contract_api.infrastructure.repositories.service_repository import OffchainServiceConfigRepository

utils = Utils()
boto_utils = BotoUtils(region_name=REGION_NAME)
offchain_service_config_repo = OffchainServiceConfigRepository()
service_factory = ServiceFactory()


class RegistryService:
    def __init__(self, org_id, service_id):
        self.org_id = org_id
        self.service_id = service_id



    def publish_offline_assets(self, attributes):
        # publish demo component file
        if attributes.get("demo_component_url", ""):
            new_demo_url = self.publish_demo_component(attributes["demo_component_url"])
            attributes.update({"demo_component_status": "PENDING"})
            attributes.update({"demo_component_url": new_demo_url})
            attributes.update({"demo_component_last_updated": str(dt.utcnow())})
        return attributes

    def save_offchain_service_attribute(self, new_offchain_attributes):
        existing_offchain_attributes = offchain_service_config_repo.get_offchain_service_config(self.org_id,
                                                                                                self.service_id)
        demo_component = self.create_or_update_demo_component_domain_model(new_offchain_attributes,
                                                                           existing_offchain_attributes.to_dict()[
                                                                               "attributes"])
        existing_offchain_attributes.attributes = demo_component.to_dict()
        offchain_service_attribute = offchain_service_config_repo.save_offchain_service_attribute(
            existing_offchain_attributes)
        return offchain_service_attribute.to_dict()

    def create_or_update_demo_component_domain_model(self, new_offchain_attributes, existing_offchain_attributes):
        existing_demo_component = service_factory.create_demo_component_domain_model(existing_offchain_attributes)
        if existing_demo_component:
            demo_component = existing_demo_component
            if new_offchain_attributes.get("demo_component_required", None) is not None:
                demo_component.demo_component_required = new_offchain_attributes.get("demo_component_required")
        else:
            demo_component = DemoComponent(
                demo_component_required=new_offchain_attributes["demo_component_required"]
            )
        if demo_component.demo_component_required:
            if new_offchain_attributes["demo_component_url"]:
                demo_component.demo_component_url = self.publish_demo_component(
                    demo_component.demo_component_url
                )
                demo_component.demo_component_status = BuildStatus.PENDING
                demo_component.demo_component_last_modified = str(dt.utcnow())
        return demo_component

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
