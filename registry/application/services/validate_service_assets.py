import json
import os

from common import utils
from common.boto_utils import BotoUtils
from common.logger import get_logger
from registry.config import REGION_NAME, DEMO_COMPONENT_CODE_BUILD_NAME, \
    UPDATE_DEMO_COMPONENT_BUILD_STATUS_LAMBDA_ARN, MANAGE_PROTO_COMPILATION_LAMBDA_ARN, ALLOWED_HERO_IMAGE_FORMATS
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository

logger = get_logger(__name__)
boto_utils = BotoUtils(region_name=REGION_NAME)
service_repo = ServicePublisherRepository()


class ValidateServiceAssets:
    def __init__(self):
        pass

    @staticmethod
    def validate_service_assets(payload):
        uploaded_file_path = payload["Records"][0]['s3']['object']['key']
        bucket_name = payload["Records"][0]['s3']['bucket']['name']
        name, extension = os.path.splitext(uploaded_file_path)
        if uploaded_file_path.endswith('_component.zip'):
            return ValidateServiceAssets.trigger_demo_component_code_build(uploaded_file_path, bucket_name)
        elif uploaded_file_path.endswith('_proto_files.zip'):
            ValidateServiceAssets.validate_proto(uploaded_file_path, bucket_name)
        elif extension[1:] in ALLOWED_HERO_IMAGE_FORMATS:
            ValidateServiceAssets.update_hero_image_url(uploaded_file_path, bucket_name)

    @staticmethod
    def trigger_demo_component_code_build(file_path, bucket_name):
        try:
            org_uuid, service_uuid, filename, s3_url = ValidateServiceAssets.extract_file_details_from_file_path(
                path=file_path,
                bucket_name=bucket_name,
                file_type='demo_component'
            )
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
            ValidateServiceAssets.update_demo_component_details(org_uuid=org_uuid, service_uuid=service_uuid,
                                                                build_id=build_id, url=s3_url, bucket_name=bucket_name)
            return {'build_id': build_id}
        except Exception as e:
            raise e

    @staticmethod
    def update_demo_component_details(org_uuid, service_uuid, build_id, url, bucket_name):
        service = service_repo.get_service_for_given_service_uuid(org_uuid=org_uuid, service_uuid=service_uuid)
        if service:
            assets = service.assets
            demo_details = assets['demo_files']
            demo_details.update({'build_id': build_id})
            demo_details.update({'url': url})
            demo_details.update({'status': "PENDING"})
            assets.update({'demo_files': demo_details})
        else:
            raise Exception(f"Service {service_uuid} not found for org {org_uuid}")
        service_repo.save_service(username=f"S3::{bucket_name}", service=service, state=service.service_state.state)

    @staticmethod
    def update_demo_component_build_status(org_uuid, service_uuid, build_status, build_id, filename):
        status = "SUCCEEDED" if int(build_status) else "FAILED"
        service = service_repo.get_service_for_given_service_uuid(org_uuid=org_uuid, service_uuid=service_uuid)
        if service:
            assets = service.assets
            demo_details = assets['demo_files']
            if ValidateServiceAssets.validate_demo_component_details(demo_details, build_id, filename):
                demo_details.update({'status': status})
                assets.update({'demo_files': demo_details})
        else:
            raise Exception(f"Service {service_uuid} not found for org {org_uuid}")
        service_repo.save_service(username=f"CodeBuild", service=service, state=service.service_state.state)

    @staticmethod
    def validate_demo_component_details(demo_details, build_id, filename):
        demo_filename = os.path.basename(demo_details.get("url", ""))
        demo_build_id = demo_details.get("build_id", "")
        logger.info(f"prev build_id {demo_build_id} new build_id {build_id}")
        logger.info(f"prev filename {demo_filename} new filename {filename}")
        if demo_build_id == build_id and demo_filename == filename:
            return True
        return False

    @staticmethod
    def validate_proto(file_path, bucket_name):
        org_uuid, service_uuid, filename, s3_url = ValidateServiceAssets.extract_file_details_from_file_path(
            path=file_path,
            bucket_name=bucket_name,
            file_type='proto'
        )
        payload = {
            "input_s3_path": f"s3://{bucket_name}/{file_path}",
            "output_s3_path": ""
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
        ValidateServiceAssets.update_proto_status(org_uuid, service_uuid, status, s3_url)

    @staticmethod
    def update_proto_status(org_uuid, service_uuid, status, filename):
        service = service_repo.get_service_for_given_service_uuid(org_uuid=org_uuid, service_uuid=service_uuid)
        if service:
            assets = service.assets
            proto_details = assets['proto_files']
            proto_details.update({'status': status})
            proto_details.update({'url': filename})
            assets.update({'proto_files': proto_details})
        else:
            # Notify user for bad demo component files
            pass
        service_repo.save_service(username=f"CodeBuild :: {DEMO_COMPONENT_CODE_BUILD_NAME}", service=service,
                                  state=service.service_state.state)

    @staticmethod
    def update_hero_image_url(file_path, bucket_name):
        org_uuid, service_uuid, filename, s3_url = ValidateServiceAssets.extract_file_details_from_file_path(
            path=file_path,
            bucket_name=bucket_name,
            file_type='hero_image'
        )
        service = service_repo.get_service_for_given_service_uuid(org_uuid=org_uuid, service_uuid=service_uuid)
        if service:
            assets = service.assets
            hero_image = assets['hero_image']
            hero_image.update({'url': s3_url})
            assets.update({'hero_image': hero_image})
        service_repo.save_service(username=f"S3::{bucket_name}", service=service,
                                  state=service.service_state.state)

    @staticmethod
    def extract_file_details_from_file_path(path, bucket_name, file_type):
        if file_type == 'proto':
            if not utils.match_regex_string(path=path, regex_pattern="([a-zA-Z0-9_]*(\/services\/)[a-zA-Z0-9_]*(\/proto\/)[^\/.]*(_proto_files.zip))"):
                msg = f"proto Component file path {path} is not valid."
                logger.info(msg)
                raise Exception(msg)
        if file_type == 'demo_component':
            if not utils.match_regex_string(path=path, regex_pattern="([a-zA-Z0-9_]*(\/services\/)[a-zA-Z0-9_]*(\/component\/)[^\/.]*(_component.zip))"):
                msg = f"Demo Component file path {path} is not valid."
                logger.info(msg)
                raise Exception(msg)
        if file_type == 'hero_image':
            pattern = "([a-zA-Z0-9_]*(\/services\/)[a-zA-Z0-9_]*(\/assets\/)[^\/.]*([^?#]*\.(?:{"+ '|'.join(ALLOWED_HERO_IMAGE_FORMATS) +"})))"
            if not utils.match_regex_string(path=path, regex_pattern=pattern):
                msg = f"Hero image file path {path} is not valid."
                logger.info(msg)
                raise Exception(msg)
        path_values = path.split('/')
        s3_url = f"https://{bucket_name}.s3.{REGION_NAME}.amazonaws.com/{path}"
        return path_values[0], path_values[2], path_values[4], s3_url
