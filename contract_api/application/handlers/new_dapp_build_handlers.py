from common.constant import StatusCode
from common.logger import get_logger
from common.repository import Repository
from common.utils import Utils, generate_lambda_response
from contract_api.application.services.update_assets_service import UpdateServiceAssets
from contract_api.config import NETWORK_ID, NETWORKS
from contract_api.application.services.registry import Registry

db = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
obj_util = Utils()
logger = get_logger(__name__)


def trigger_dapp_build(event, context):
    logger.info(f"trigger_demo_component_build event :: {event}")
    response = UpdateServiceAssets().trigger_dapp_build(payload = event)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )


def notify_deploy_status(event, context):
    logger.info(f"Service Build status event {event}")
    org_id = event['org_id']
    service_id = event['service_id']
    build_status = int(event['build_status'])
    Registry(obj_repo = db).notify_build_status(org_id, service_id, build_status)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": "Build failure notified", "error": {}}, cors_enabled = True
    )
