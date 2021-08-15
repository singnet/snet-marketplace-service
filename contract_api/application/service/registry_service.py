from common.utils import Utils
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
            tar_file_path = utils.extract_zip_and_and_tar(attributes["demo_component_url"])
            key = f"assets/{self.org_id}/{self.service_id}/component.tar.gz"
            boto_utils.s3_upload_file(filename=tar_file_path, bucket=ASSETS_COMPONENT_BUCKET_NAME, key=key)
            attributes.update({"demo_component_status": "PENDING"})
            attributes.update({"demo_component_url": f"https://{ASSETS_COMPONENT_BUCKET_NAME}.s3.amazonaws.com/{key}"})
        return attributes
