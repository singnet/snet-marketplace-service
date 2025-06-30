from typing import Any

from common.utils import get_logger
from common import utils
from common.boto_utils import BotoUtils
from common.constant import BuildStatus
from common.exceptions import InvalidFilePath
from contract_api.application.schemas.dapp_build_schemas import TriggerDappBuildRequest, NotifyDeployStatusRequest
from contract_api.config import REGION_NAME, MARKETPLACE_DAPP_BUILD
from contract_api.constant import ServiceAssetsRegex, BuildCode
from contract_api.domain.models.offchain_service_attribute import OffchainServiceConfigDomain
from contract_api.exceptions import BuildTriggerFailedException, UpsertOffchainConfigsFailedException, \
    ServiceCurationFailedException
from contract_api.infrastructure.repositories.service_repository import ServiceRepository

logger = get_logger(__name__)


class DappBuildService:
    def __init__(self):
        self._boto_utils = BotoUtils(REGION_NAME)
        self._service_repo = ServiceRepository()

    def trigger_dapp_build(self, request: TriggerDappBuildRequest) -> Any:
        file_path = request.file_path

        org_id, service_id = self._extract_file_details_from_file_path(file_path = file_path)
        variables = {"org_id": org_id, "service_id": service_id}
        env_variables = []
        for variable in variables:
            env_variables.append({"name": variable, "type": "PLAINTEXT", "value": variables[variable]})
        build_details = {
            'projectName': MARKETPLACE_DAPP_BUILD,
            'environmentVariablesOverride': env_variables
        }
        try:
            build_trigger_response = self._boto_utils.trigger_code_build(build_details = build_details)
        except Exception:
            raise BuildTriggerFailedException()
        build_id = build_trigger_response['build']['id']
        logger.info(f"Build triggered details :: {build_details} build_id :: {build_id}")
        return build_id

    def notify_build_status(self, request: NotifyDeployStatusRequest) -> dict:
        org_id = request.org_id
        service_id = request.service_id
        build_status = request.build_status
        is_curated = False

        if build_status == BuildCode.SUCCESS:
            is_curated = True

        try:
            self._service_repo.curate_service(org_id, service_id, is_curated)
        except Exception:
            raise ServiceCurationFailedException(org_id = org_id, service_id = service_id)

        demo_build_status = BuildStatus.SUCCESS if build_status == BuildCode.SUCCESS else BuildStatus.FAILED
        offchain_attributes = OffchainServiceConfigDomain(
            row_id=0, # dummy
            org_id=org_id,
            service_id=service_id,
            parameter_name = "demo_component_build_status",
            parameter_value = demo_build_status
        )
        try:
            self._service_repo.upsert_offchain_service_config(org_id, service_id, [offchain_attributes])
        except Exception:
            raise UpsertOffchainConfigsFailedException(org_id = org_id, service_id = service_id)

        return {}

    @staticmethod
    def _extract_file_details_from_file_path(file_path) -> tuple[str, str]:
        if utils.match_regex_string(path = file_path, regex_pattern = ServiceAssetsRegex.DEMO_FILE_PATH.value):
            path_values = file_path.split('/')
            return path_values[1], path_values[2]
        else:
            raise InvalidFilePath(file_path = file_path)