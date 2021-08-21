import json
import os.path
from datetime import datetime as dt

from common import utils
from common.boto_utils import BotoUtils
from common.logger import get_logger
from registry.config import REGION_NAME, DEMO_COMPONENT_CODE_BUILD_NAME, \
    MANAGE_PROTO_COMPILATION_LAMBDA_ARN, UPDATE_DEMO_COMPONENT_BUILD_STATUS_LAMBDA_ARN
from registry.constants import ServiceStatus, ServiceAssetsRegex
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository

logger = get_logger(__name__)
boto_utils = BotoUtils(region_name=REGION_NAME)
service_repo = ServicePublisherRepository()


class UpdateServiceAssets:
    def __init__(self):
        pass

    @staticmethod
    def validate_and_process_service_assets(payload):
        file_path = payload["Records"][0]['s3']['object']['key']
        bucket_name = payload["Records"][0]['s3']['bucket']['name']
        org_uuid, service_uuid, filename = UpdateServiceAssets. \
            extract_file_details_from_file_path(file_path=file_path)
        service = service_repo.get_service_for_given_service_uuid(org_uuid=org_uuid, service_uuid=service_uuid)
        if not service:
            raise Exception(f"Service with org_uuid {org_uuid} and service_uuid {service_uuid} not found")
        if utils.match_regex_string(path=file_path, regex_pattern=ServiceAssetsRegex.PROTO_FILE_URL.value):
            proto_compile_status = UpdateServiceAssets.validate_proto(file_path, bucket_name, org_uuid=org_uuid, service_uuid=service_uuid)
            proto_details = {
                "url": f"https://{bucket_name}.s3.{REGION_NAME}.amazonaws.com/{file_path}",
                "status": proto_compile_status
            }
            service.assets.update({"proto_files": proto_details})
            response = {}
        elif utils.match_regex_string(path=file_path, regex_pattern=ServiceAssetsRegex.DEMO_COMPONENT_URL.value):
            build_id = UpdateServiceAssets.trigger_demo_component_code_build(org_uuid=org_uuid,
                                                                             service_uuid=service_uuid,
                                                                             filename=filename)
            demo_details = service.assets.get("demo_details", {})
            demo_details.update({"url": f"https://{bucket_name}.s3.{REGION_NAME}.amazonaws.com/{file_path}"})
            demo_details.update({"build_id": build_id})
            demo_details.update({"status": "PENDING"})
            demo_details.update({"last_modified": dt.isoformat(dt.utcnow())})
            service.assets.update({"demo_files": demo_details})
            response = {'build_id': build_id}
        elif utils.match_regex_string(path=file_path, regex_pattern=ServiceAssetsRegex.HERO_IMAGE_URL.value):
            hero_image_details = {
                "url": f"https://{bucket_name}.s3.{REGION_NAME}.amazonaws.com/{file_path}"
            }
            service.assets.update({"hero_image": hero_image_details})
            response = {}
        else:
            raise Exception(f"Invalid file :: {file_path}")
        service_repo.save_service(username=f"Lambda|update-service-assets", service=service, state=service.service_state.state)
        return response

    @staticmethod
    def extract_file_details_from_file_path(file_path):
        if utils.match_regex_string(path=file_path, regex_pattern=ServiceAssetsRegex.COMMON_FILE_PATH.value):
            path_values = file_path.split('/')
            return path_values[0], path_values[2], os.path.basename(file_path)
        else:
            raise Exception(f"Invalid file path :: {file_path}")

    @staticmethod
    def trigger_demo_component_code_build(org_uuid, service_uuid, filename):
        lambda_function = UPDATE_DEMO_COMPONENT_BUILD_STATUS_LAMBDA_ARN
        variables = ["org_uuid", "service_uuid", "filename", "lambda_function"]
        env_variables = []
        for variable in variables:
            env_variables.append({"name": variable, "type": "PLAINTEXT", "value": eval(variable)})
        build_details = {
            'projectName': DEMO_COMPONENT_CODE_BUILD_NAME,
            'environmentVariablesOverride': env_variables
        }
        build_trigger_response = boto_utils.trigger_code_build(build_details=build_details)
        build_id = build_trigger_response['build']['id']
        logger.info(f"Build triggered details :: {build_details} build_id :: {build_id}")
        return build_id

    @staticmethod
    def validate_proto(file_path, bucket_name, org_uuid, service_uuid):
        payload = {
            "input_s3_path": f"s3://{bucket_name}/{file_path}",
            "output_s3_path": "",
            "org_id": org_uuid,
            "service_id": service_uuid
        }
        response = boto_utils.invoke_lambda(
            payload=json.dumps(payload),
            invocation_type="RequestResponse",
            lambda_function_arn=MANAGE_PROTO_COMPILATION_LAMBDA_ARN
        )
        if response['statusCode'] == 200:
            status = 'SUCCEEDED'
        else:
            status = "FAILED"
        return status

    # update_demo_component_build_status LAMBDA

    @staticmethod
    def update_demo_component_build_status(org_uuid, service_uuid, build_status, build_id, filename):
        status = "SUCCEEDED" if int(build_status) else "FAILED"
        service = service_repo.get_service_for_given_service_uuid(org_uuid=org_uuid, service_uuid=service_uuid)
        if service:
            assets = service.assets
            demo_details = assets['demo_files']
            if UpdateServiceAssets.validate_demo_component_details(demo_details, build_id, filename):
                demo_details.update({'status': status})
                assets.update({'demo_files': demo_details})
                if status == "SUCCEEDED":
                    next_state = ServiceStatus.APPROVED.value
                else:
                    next_state = ServiceStatus.CHANGE_REQUESTED.value
                service_repo.save_service(username=f"CodeBuild :: {DEMO_COMPONENT_CODE_BUILD_NAME}", service=service,
                                          state=next_state)
        else:
            raise Exception(f"Service {service_uuid} not found for org {org_uuid}")

    @staticmethod
    def validate_demo_component_details(demo_details, build_id, filename):
        demo_filename = os.path.basename(demo_details.get("url", ""))
        demo_build_id = demo_details.get("build_id", "")
        logger.info(f"prev build_id {demo_build_id} new build_id {build_id}")
        logger.info(f"prev filename {demo_filename} new filename {filename}")
        if demo_build_id == build_id and demo_filename == filename:
            return True
        return False

    # update_demo_component_build_status LAMBDA
