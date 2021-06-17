import re

from common import utils
from common.boto_utils import BotoUtils
from common.logger import get_logger
from registry.config import REGION_NAME, COMPONENT_PATH_VALIDATION_PATTERN, COMPONENT_CODE_BUILD_ID
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository
logger = get_logger(__name__)


class ValidateComponent:
    def __init__(self):
        self.boto_utils = BotoUtils(region_name=REGION_NAME)
        self.service_repo = ServicePublisherRepository()

    def trigger_demo_component_code_build(self, payload):
        try:
            uploaded_file_path = payload["Records"][0]['s3']['object']['key']
            service_details = self.validate_uploaded_file(uploaded_file_path=uploaded_file_path)

            build_details = {
                'projectName': COMPONENT_CODE_BUILD_ID,
                'environmentVariablesOverride': [
                    {
                        'name': 'org_uuid',
                        'value': f"{service_details['org_uuid']}",
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'service_uuid',
                        'value': f"{service_details['service_uuid']}",
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'filename',
                        'value': f"{service_details['filename']}",
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'lambda_function',
                        'value': f" ",
                        'type': 'PLAINTEXT'
                    }
                ]
            }
            build_trigger_response = self.boto_utils.trigger_code_build(build_details=build_details)
            build_id = build_trigger_response['build']['id']
            self.update_demo_trigger_id_to_service(org_uuid=service_details['org_uuid'], service_uuid=service_details['service_uuid'], build_id=build_id)
            return {'build_id': build_id}
        except Exception as e:
            raise e

    def update_demo_trigger_id_to_service(self, org_uuid, service_uuid, build_id):
        service = self.service_repo.get_service_for_given_service_uuid(org_uuid=org_uuid, service_uuid=service_uuid)
        if service:
            assets = service.assets
            demo_details = assets['demo_files']
            demo_details.update({'build_id': build_id})
            assets.update({'demo_files': demo_details})
        else:
            raise Exception(f"Service {service_uuid} not found for org {org_uuid}")
        self.service_repo.update_service(org_uuid=org_uuid, service_uuid=service_uuid, assets=assets)

    def validate_uploaded_file(self, uploaded_file_path):
        if not utils.match_regex_string(path=uploaded_file_path, regex_pattern=COMPONENT_PATH_VALIDATION_PATTERN):
            msg = f"Uploaded file's path {uploaded_file_path} does not match to trigger code build"
            logger.info(msg)
            raise Exception(msg)
        path_values = uploaded_file_path.split('/')
        service_details = {
            "org_uuid": path_values[0],
            "service_uuid": path_values[2],
            "filename": path_values[4]
        }
        return service_details



