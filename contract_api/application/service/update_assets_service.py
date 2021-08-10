import boto3

from common import utils
from common.boto_utils import BotoUtils
from common.logger import get_logger
from contract_api.config import MARKETPLACE_DAPP_BUILD, REGION_NAME
from contract_api.constant import ServiceAssetsRegex

logger = get_logger(__name__)
boto_utils = BotoUtils(region_name=REGION_NAME)


class UpdateServiceAssets:
    pass

    @staticmethod
    def trigger_demo_component_build(payload):
        file_path = payload["Records"][0]['s3']['object']['key']
        bucket_name = payload["Records"][0]['s3']['bucket']['name']
        org_id, service_id = UpdateServiceAssets.extract_file_details_from_file_path(file_path=file_path)
        variables = ["org_id", "service_id"]
        env_variables = []
        for variable in variables:
            env_variables.append({"name": variable, "type": "PLAINTEXT", "value": eval(variable)})
        build_details = {
            'projectName': MARKETPLACE_DAPP_BUILD,
            'environmentVariablesOverride': env_variables
        }
        build_trigger_response = boto_utils.trigger_code_build(build_details=build_details)
        build_id = build_trigger_response['build']['id']
        logger.info(f"Build triggered details :: {build_details} build_id :: {build_id}")
        return build_id

    def extract_file_details_from_file_path(file_path):
        if utils.match_regex_string(path=file_path, regex_pattern=ServiceAssetsRegex.DEMO_FILE_PATH.value):
            path_values = file_path.split('/')
            return path_values[1], path_values[2]
        else:
            raise Exception(f"Invalid file path :: {file_path}")

