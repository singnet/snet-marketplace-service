from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response

from contract_api.application.schemas.dapp_build_schemas import TriggerDappBuildRequest, NotifyDeployStatusRequest
from contract_api.application.services.dapp_build_service import DappBuildService


logger = get_logger(__name__)


@exception_handler(logger=logger)
def trigger_dapp_build(event, context):
    request = TriggerDappBuildRequest.validate_event(event)

    response = DappBuildService().trigger_dapp_build(request)

    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )


@exception_handler(logger=logger)
def notify_deploy_status(event, context):
    request = NotifyDeployStatusRequest.validate_event(event)

    DappBuildService().notify_build_status(request)

    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": "Build failure notified", "error": {}}, cors_enabled = True
    )
