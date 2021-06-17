from common import utils
from common.boto_utils import BotoUtils
from common.logger import get_logger
from registry.config import REGION_NAME, COMPONENT_PATH_VALIDATION_PATTERN, DEMO_COMPONENT_CODE_BUILD_NAME, \
    UPDATE_DEMO_COMPONENT_BUILD_STATUS_LAMBDA_ARN
from registry.constants import ServiceStatus
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository

logger = get_logger(__name__)
boto_utils = BotoUtils(region_name=REGION_NAME)
service_repo = ServicePublisherRepository()


class ValidateDemoComponent:
    def __init__(self):
        pass

    @staticmethod
    def trigger_demo_component_code_build(payload):
        try:
            uploaded_file_path = payload["Records"][0]['s3']['object']['key']
            org_uuid, service_uuid, filename = ValidateDemoComponent().extract_file_details_from_file_path(
                path=uploaded_file_path)
            build_details = {
                'projectName': DEMO_COMPONENT_CODE_BUILD_NAME,
                'environmentVariablesOverride': [
                    {
                        'name': 'org_uuid',
                        'value': f"{org_uuid}",
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'service_uuid',
                        'value': f"{service_uuid}",
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'filename',
                        'value': f"{filename}",
                        'type': 'PLAINTEXT'
                    },
                    {
                        'name': 'lambda_function',
                        'value': UPDATE_DEMO_COMPONENT_BUILD_STATUS_LAMBDA_ARN,
                        'type': 'PLAINTEXT'
                    }
                ]
            }
            build_trigger_response = boto_utils.trigger_code_build(build_details=build_details)
            build_id = build_trigger_response['build']['id']
            ValidateDemoComponent().update_demo_code_build_id(org_uuid=org_uuid, service_uuid=service_uuid,
                                                              build_id=build_id)
            return {'build_id': build_id}
        except Exception as e:
            raise e

    @staticmethod
    def update_demo_code_build_id(org_uuid, service_uuid, build_id):
        service = service_repo.get_service_for_given_service_uuid(org_uuid=org_uuid, service_uuid=service_uuid)
        if service:
            assets = service.assets
            demo_details = assets['demo_files']
            demo_details.update({'build_id': build_id})
            demo_details.update({'status': "PENDING"})
            assets.update({'demo_files': demo_details})
        else:
            raise Exception(f"Service {service_uuid} not found for org {org_uuid}")
        service_repo.update_service_assets(org_uuid=org_uuid, service_uuid=service_uuid, assets=assets)

    @staticmethod
    def extract_file_details_from_file_path(path):
        if not utils.match_regex_string(path=path, regex_pattern=COMPONENT_PATH_VALIDATION_PATTERN):
            msg = f"Demo Component file path {path} is not valid."
            logger.info(msg)
            raise Exception(msg)
        path_values = path.split('/')
        return path_values[0], path_values[2], path_values[4]

    @staticmethod
    def update_demo_component_build_status(org_uuid, service_uuid, build_status):
        status = "SUCCEEDED" if build_status else "FAILED"
        service = service_repo.get_service_for_given_service_uuid(org_uuid=org_uuid, service_uuid=service_uuid)
        if service:
            assets = service.assets
            demo_details = assets['demo_files']
            demo_details.update({'status': status})
            assets.update({'demo_files': demo_details})
        else:
            raise Exception(f"Service {service_uuid} not found for org {org_uuid}")
        service_repo.update_service_assets(org_uuid=org_uuid, service_uuid=service_uuid, assets=assets)
        if status == "SUCCEEDED":
            service_repo.update_service_status(
                service_uuid_list=[service_uuid],
                prev_state=ServiceStatus.APPROVAL_PENDING.value,
                next_state=ServiceStatus.APPROVED.value
            )
