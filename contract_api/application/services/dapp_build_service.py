from common import utils
from common.constant import BuildStatus


class DappBuildService:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_utils = Utils()

    # is used in handler
    @staticmethod
    def trigger_dapp_build(payload):
        file_path = payload["Records"][0]['s3']['object']['key']
        org_id, service_id = UpdateServiceAssets._extract_file_details_from_file_path(file_path = file_path)
        variables = {"org_id": org_id, "service_id": service_id}
        env_variables = []
        for variable in variables:
            env_variables.append({"name": variable, "type": "PLAINTEXT", "value": variables[variable]})
        build_details = {
            'projectName': MARKETPLACE_DAPP_BUILD,
            'environmentVariablesOverride': env_variables
        }
        build_trigger_response = boto_utils.trigger_code_build(build_details = build_details)
        build_id = build_trigger_response['build']['id']
        logger.info(f"Build triggered details :: {build_details} build_id :: {build_id}")
        return build_id

    # is used in handler
    @staticmethod
    def notify_build_status(org_id, service_id, build_status):
        is_curated = False
        if build_status == BUILD_CODE['SUCCESS']:
            is_curated = True
        service = new_service_repo.get_service(org_id = org_id, service_id = service_id)
        if service:
            service.is_curated = is_curated
            new_service_repo.create_or_update_service(service = service)
        else:
            raise Exception(f"Unable to find service for service_id {service_id} and org_id {org_id}")
        demo_build_status = BuildStatus.SUCCESS if build_status == BUILD_CODE['SUCCESS'] else BuildStatus.FAILED
        offchain_attributes = OffchainServiceAttribute(
            org_id, service_id, {"demo_component_status": demo_build_status}
        )
        OffchainServiceConfigRepository().save_offchain_service_attribute(offchain_attributes)

    @staticmethod
    def _extract_file_details_from_file_path(file_path):
        if utils.match_regex_string(path = file_path, regex_pattern = ServiceAssetsRegex.DEMO_FILE_PATH.value):
            path_values = file_path.split('/')
            return path_values[1], path_values[2]
        else:
            raise InvalidFilePath(file_path = file_path)